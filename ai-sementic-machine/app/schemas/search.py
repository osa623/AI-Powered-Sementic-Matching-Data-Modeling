from pydantic import BaseModel
from typing import List, Optional

class SearchQuery(BaseModel):
    text: str
    category: Optional[str] = None
    limit: Optional[int] = 10

class MatchResult(BaseModel):
    id: str
    description: str
    category: str
    score: float
    reason: str

class SearchResponse(BaseModel):
    matches: List[MatchResult]
    total_matches: int = 0
    inferred_context: List[str] = []
