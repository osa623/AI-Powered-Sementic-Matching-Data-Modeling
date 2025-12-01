import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings
import os

class SemanticEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("Loading Semantic Model...")
        try:
            self.model = SentenceTransformer(settings.MODEL_PATH)
            print("✅ Loaded Fine-Tuned Model.")
        except Exception as e:
            print(f"⚠️ Fine-tuned model not found ({e}). Loading Base Model.")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        self.dimension = 384
        
        if os.path.exists(settings.INDEX_PATH):
            self.index = faiss.read_index(settings.INDEX_PATH)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.items_metadata = []

    def vectorize(self, text: str):
        return self.model.encode([text])[0]

    def add_item(self, item_data: dict):
        # 1. Vectorize the Description (English/Singlish)
        vector = self.vectorize(item_data['description'])
        
        # 2. Add to Vector DB
        self.index.add(np.array([vector], dtype=np.float32))
        
        # 3. Store Metadata (ID, Description, Category ONLY)
        self.items_metadata.append({
            "id": item_data['id'],
            "description": item_data['description'],
            "category": item_data['category']
        })
        return True

    def search(self, query_text: str, limit: int = 5):
        query_vec = self.vectorize(query_text)
        distances, indices = self.index.search(np.array([query_vec], dtype=np.float32), limit)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.items_metadata):
                continue
            
            # Score Calculation
            score = max(0, 100 - (distances[0][i] * 15))
            
            results.append({
                "item": self.items_metadata[idx],
                "semantic_score": round(score, 2)
            })
        return results