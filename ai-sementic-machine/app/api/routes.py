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

@router.post("/index", summary="Add Item (Desc + Category)")
def index_item(item: ItemCreate, engine: SemanticEngine = Depends(get_semantic)):
    # Pass the clean dict (id, description, category) to the engine
    engine.add_item(item.dict())
    return {"message": "Item Vectorized & Indexed Successfully"}

@router.post("/search", response_model=SearchResponse, summary="Find Matches")
def search_items(
    query: SearchQuery, 
    semantic: SemanticEngine = Depends(get_semantic),
    modeling: DataModelingEngine = Depends(get_modeling)
):
    # 1. Semantic Search (Text -> Vector)
    raw_results = semantic.search(query.text)
    
    # 2. Data Modeling (Context Inference)
    context_suggestions = []
    if query.category:
        context_suggestions = modeling.get_context(query.category)

    # 3. Format Response
    formatted_matches = []
    for res in raw_results:
        formatted_matches.append(MatchResult(
            id=res['item']['id'],
            description=res['item']['description'],
            category=res['item']['category'],
            score=res['semantic_score'],
            reason="Semantic Vector Match"
        ))

    return SearchResponse(
        matches=formatted_matches,
        inferred_context=context_suggestions
    )

@router.post("/fraud-check", summary="Check User Behavior for Fraud")
def check_fraud(user_metadata: dict, fraud_engine: FraudDetectionEngine = Depends(get_fraud)):
    result = fraud_engine.predict_fraud(user_metadata)
    return result