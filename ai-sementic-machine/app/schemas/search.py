from pydantic import BaseModel
from typing import List, Optional

class SearchQuery(BaseModel):
    text: str
    category: Optional[str] = None

class MatchResult(BaseModel):
    id: str
    description: str
    category: str
    score: float
    reason: str

class SearchResponse(BaseModel):
    matches: List[MatchResult]
    inferred_context: List[str] = []
