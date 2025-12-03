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
    """Search for a LOST item against all FOUND items in database using advanced semantic matching"""
    # 1. Semantic Search (Text -> Vector) with hybrid scoring - Find similar found items
    raw_results = semantic.search(
        query.text, 
        limit=query.limit if hasattr(query, 'limit') else 10,
        category_filter=query.category if query.category else None
    )
    
    # 2. Data Modeling (Context Inference)
    context_suggestions = []
    if query.category:
        context_suggestions = modeling.get_context(query.category)

    # 3. Format Response with detailed similarity metrics
    formatted_matches = []
    for res in raw_results:
        # Build detailed reason with scoring breakdown
        reason_parts = [
            f"Raw Cosine: {res['raw_cosine_similarity']:.4f}",
            f"Vector: {res['vector_score']}%",
            f"Keyword: {res['keyword_score']}%",
            f"Formula: {res['details']['formula']}"
        ]
        if res['details']['category_boost']:
            reason_parts.append("Category Boost: +5%")
        
        reason = " | ".join(reason_parts)
        
        formatted_matches.append(MatchResult(
            id=res['item']['id'],
            description=res['item']['description'],
            category=res['item']['category'],
            score=res['semantic_score'],
            reason=reason
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