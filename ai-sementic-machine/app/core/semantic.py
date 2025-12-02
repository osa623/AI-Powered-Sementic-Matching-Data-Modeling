import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.core.database import get_database
import os
import pickle
from datetime import datetime
from typing import Optional

class SemanticEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("🤖 Loading Semantic Model...")
        try:
            self.model = SentenceTransformer(settings.MODEL_PATH)
            print("✅ Loaded Fine-Tuned Model")
        except Exception as e:
            print("📥 Loading Base Multilingual Model...")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✅ Model loaded successfully")

        self.dimension = 384
        
        # Load or create FAISS index
        if os.path.exists(settings.INDEX_PATH):
            try:
                print("📂 Loading FAISS index from disk...")
                self.index = faiss.read_index(settings.INDEX_PATH)
                print("✅ Index loaded successfully")
            except Exception as e:
                print("🆕 Creating fresh FAISS index...")
                self.index = faiss.IndexFlatL2(self.dimension)
                # Delete corrupted file
                try:
                    os.remove(settings.INDEX_PATH)
                except:
                    pass
        else:
            print("🆕 Initializing new FAISS index...")
            self.index = faiss.IndexFlatL2(self.dimension)
        
        # Load or create metadata
        if os.path.exists(settings.METADATA_PATH):
            try:
                print("📂 Loading metadata from cache...")
                with open(settings.METADATA_PATH, 'rb') as f:
                    self.items_metadata = pickle.load(f)
                print(f"✅ Loaded {len(self.items_metadata)} items from cache")
            except Exception as e:
                print("🆕 Starting with empty metadata")
                self.items_metadata = []
                # Delete corrupted file
                try:
                    os.remove(settings.METADATA_PATH)
                except:
                    pass
        else:
            self.items_metadata = []
            if len(self.items_metadata) == 0:
                print("💾 Cache is empty - will load from MongoDB")
    
    def _save_to_disk(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(settings.INDEX_PATH), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, settings.INDEX_PATH)
            
            # Save metadata
            with open(settings.METADATA_PATH, 'wb') as f:
                pickle.dump(self.items_metadata, f)
            
            print(f"💾 Saved index and metadata ({len(self.items_metadata)} items)")
        except Exception as e:
            print(f"⚠️ Could not save to disk: {e}")

    def vectorize(self, text: str):
        return self.model.encode([text])[0]

    async def add_item(self, item_data: dict):
        """Add a FOUND item to the vector database and MongoDB"""
        # 1. Vectorize the Description (English/Singlish/Sinhala)
        vector = self.vectorize(item_data['description'])
        
        # 2. Add to Vector DB (FAISS Index)
        self.index.add(np.array([vector], dtype=np.float32))
        
        # 3. Store Metadata in memory
        metadata = {
            "id": item_data['id'],
            "description": item_data['description'],
            "category": item_data['category']
        }
        self.items_metadata.append(metadata)
        
        # 4. Save to MongoDB (if available)
        try:
            db = get_database()
            if db is not None:
                document = {
                    "item_id": item_data['id'],
                    "description": item_data['description'],
                    "category": item_data['category'],
                    "vector": vector.tolist(),  # Store vector for future use
                    "created_at": datetime.utcnow(),
                    "index_position": len(self.items_metadata) - 1
                }
                await db.found_items.insert_one(document)
                print(f"💾 Saved to MongoDB: {item_data['id']}")
        except Exception as e:
            print(f"⚠️ MongoDB save failed: {e}")
        
        # 5. Persist to disk every 10 items
        if len(self.items_metadata) % 10 == 0:
            self._save_to_disk()
        
        return item_data['id']
    
    async def load_from_mongodb(self):
        """Load all items from MongoDB on startup"""
        try:
            db = get_database()
            if db is None:
                return
            
            cursor = db.found_items.find().sort("created_at", 1)
            items = await cursor.to_list(length=None)
            
            if not items:
                print("📭 No items found in MongoDB")
                return
            
            print(f"📥 Loading {len(items)} items from MongoDB...")
            
            # Clear existing data
            self.index = faiss.IndexFlatL2(self.dimension)
            self.items_metadata = []
            
            # Rebuild index from MongoDB
            for item in items:
                vector = np.array(item['vector'], dtype=np.float32)
                self.index.add(np.array([vector]))
                
                self.items_metadata.append({
                    "id": item['item_id'],
                    "description": item['description'],
                    "category": item['category']
                })
            
            # Save to disk
            self._save_to_disk()
            print(f"✅ Loaded {len(items)} items from MongoDB")
            
        except Exception as e:
            print(f"⚠️ Could not load from MongoDB: {e}")

    def search(self, query_text: str, limit: int = 10):
        """Search for LOST item description against all FOUND items using semantic similarity"""
        if len(self.items_metadata) == 0:
            return []
        
        # Vectorize the LOST item description
        query_vec = self.vectorize(query_text)
        
        # Search in FAISS index for similar FOUND items
        k = min(limit, len(self.items_metadata))
        distances, indices = self.index.search(np.array([query_vec], dtype=np.float32), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.items_metadata):
                continue
            
            # Calculate similarity percentage (convert L2 distance to similarity score)
            # Lower distance = higher similarity
            distance = distances[0][i]
            
            # Convert distance to similarity percentage (0-100%)
            # Using exponential decay for better score distribution
            similarity_percentage = max(0, min(100, 100 * np.exp(-distance / 2)))
            
            results.append({
                "item": self.items_metadata[idx],
                "semantic_score": round(similarity_percentage, 2),
                "distance": round(float(distance), 4)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['semantic_score'], reverse=True)
        return results