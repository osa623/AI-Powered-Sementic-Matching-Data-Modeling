from fastapi import FastAPI
from typing import List
from .engine import SemanticEngine
from .schemas import ItemCreate, SearchQuery, SearchResult

app = FastAPI(title="Lost & Found Semantic Engine")
engine = SemanticEngine()

@app.get("/")
def home():
    return {"status": "AI Engine Active", "message": "Go to /docs to test"}

@app.post("/add_item")
def add_item(item: ItemCreate):
    engine.add_item(item.dict())
    return {"message": "Item indexed successfully"}

@app.post("/search", response_model=List[SearchResult])
def search_items(query: SearchQuery):
    results = engine.search(query.text, query.category)
    return results