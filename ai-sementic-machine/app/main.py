from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.semantic import SemanticEngine

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    """Startup: Connect to MongoDB and load items"""
    print("🚀 Starting AI Semantic Engine...")
    await connect_to_mongo()
    
    # Load items from MongoDB into FAISS
    semantic_engine = SemanticEngine()
    await semantic_engine.load_from_mongodb()
    
    print("✅ System ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown: Close MongoDB connection"""
    print("🛑 Shutting down...")
    await close_mongo_connection()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(routes.router)

@app.get("/")
def health_check():
    return {"status": "online", "module": "Semantic & Data Modeling"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)