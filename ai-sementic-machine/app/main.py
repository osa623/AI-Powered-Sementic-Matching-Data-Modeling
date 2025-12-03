from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, is_mongodb_connected
from app.core.semantic import SemanticEngine
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    """Startup: Connect to MongoDB and load items with proper sequencing"""
    logger.info("🚀 Starting AI Semantic Engine...")
    
    # STEP 1: Establish MongoDB connection with retry logic
    logger.info("📡 Step 1/3: Connecting to MongoDB...")
    connection_success = await connect_to_mongo()
    
    if not connection_success:
        logger.warning("⚠️ MongoDB connection failed - running in standalone mode")
    else:
        logger.info("✅ MongoDB connection established")
    
    # STEP 2: Initialize Semantic Engine (loads model and creates FAISS index)
    logger.info("🤖 Step 2/3: Initializing Semantic Engine...")
    semantic_engine = SemanticEngine()
    logger.info("✅ Semantic Engine initialized")
    
    # STEP 3: Load data from MongoDB ONLY if connected
    if connection_success and is_mongodb_connected():
        logger.info("📥 Step 3/3: Loading vectors from MongoDB...")
        try:
            items_loaded = await semantic_engine.load_from_mongodb()
            logger.info(f"✅ Loaded {items_loaded} items from MongoDB")
        except Exception as e:
            logger.error(f"❌ Failed to load from MongoDB: {e}")
            logger.info("💾 Falling back to disk cache")
    else:
        logger.info("💾 Step 3/3: Using disk cache (MongoDB not available)")
    
    logger.info("✅ System ready! All initialization steps completed.")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown: Close MongoDB connection"""
    logger.info("🛑 Shutting down...")
    await close_mongo_connection()
    logger.info("👋 Shutdown complete")

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