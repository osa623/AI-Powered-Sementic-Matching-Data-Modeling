from pydantic import BaseModel
from typing import List, Optional

class ItemCreate(BaseModel):
    id: str
    description: str
    category: str

class SearchQuery(BaseModel):
    text: str
    category: Optional[str] = None

class SearchResult(BaseModel):
    id: str
    description: str
    category: str
    confidence: float