import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

class SemanticEngine:
    def __init__(self):
        # Path management to find the model
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "../data/models/fine_tuned_bert")
        
        try:
            print(f"Loading model from: {model_path}")
            self.model = SentenceTransformer(model_path)
            print("✅ Fine-Tuned Model Loaded.")
        except:
            print("⚠️ Warning: Fine-tuned model not found. Using Base Model.")
            print("   (Did you run 'python scripts/train_semantic.py'?)")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.items = [] 

    def add_item(self, item_data: dict):
        # Convert text to vector
        vector = self.model.encode([item_data['description']])
        # Add to FAISS
        self.index.add(np.array(vector, dtype=np.float32))
        # Store data
        self.items.append(item_data)
        return True

    def search(self, query_text: str, category_filter: str = None, limit: int = 5):
        query_vector = self.model.encode([query_text])
        
        # Search FAISS (get top 10 to allow filtering)
        distances, indices = self.index.search(np.array(query_vector, dtype=np.float32), k=10)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.items): continue
            
            item = self.items[idx]
            
            # Category Filter
            if category_filter and item['category'].lower() != category_filter.lower():
                continue
            
            # Score Calculation
            score = max(0, 100 - (distances[0][i] * 20)) # Simple scaling
            
            results.append({
                "id": item['id'],
                "description": item['description'],
                "category": item['category'],
                "confidence": round(score, 2)
            })
            
            if len(results) >= limit:
                break
                
        return results