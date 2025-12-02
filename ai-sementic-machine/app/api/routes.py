from fastapi import APIRouter, Depends
from app.schemas.item import ItemCreate
from app.schemas.search import SearchQuery, SearchResponse, MatchResult
from app.core.semantic import SemanticEngine
from app.core.modeling import DataModelingEngine
from app.core.fraud import FraudDetectionEngine

router = APIRouter()

# Dependency Injection
def get_semantic():
    return SemanticEngine()

def get_modeling():
    return DataModelingEngine()

def get_fraud():
    return FraudDetectionEngine()

@router.post("/index", summary="Add Found Item to Database")
async def index_item(item: ItemCreate, engine: SemanticEngine = Depends(get_semantic)):
    """Add a FOUND item to the database for future matching"""
    item_id = await engine.add_item(item.dict())
    return {
        "message": "Found item added successfully",
        "item_id": item_id,
        "status": "indexed"
    }

@router.post("/search", response_model=SearchResponse, summary="Search for Lost Item")
def search_items(
    query: SearchQuery, 
    semantic: SemanticEngine = Depends(get_semantic),
    modeling: DataModelingEngine = Depends(get_modeling)
):
    """Search for a LOST item against all FOUND items in database using semantic matching"""
    # 1. Semantic Search (Text -> Vector) - Find similar found items
    raw_results = semantic.search(query.text, limit=query.limit if hasattr(query, 'limit') else 10)
    
    # Filter by category if provided
    if query.category:
        raw_results = [r for r in raw_results if r['item']['category'].lower() == query.category.lower()]
    
    # 2. Data Modeling (Context Inference)
    context_suggestions = []
    if query.category:
        context_suggestions = modeling.get_context(query.category)

    # 3. Format Response with similarity percentages
    formatted_matches = []
    for res in raw_results:
        formatted_matches.append(MatchResult(
            id=res['item']['id'],
            description=res['item']['description'],
            category=res['item']['category'],
            score=res['semantic_score'],
            reason="AI Semantic Vector Similarity"
        ))

    return SearchResponse(
        matches=formatted_matches,
        total_matches=len(formatted_matches),
        inferred_context=context_suggestions
    )

@router.post("/fraud-check", summary="Check User Behavior for Fraud")
def check_fraud(user_metadata: dict, fraud_engine: FraudDetectionEngine = Depends(get_fraud)):
    result = fraud_engine.predict_fraud(user_metadata)
    return result