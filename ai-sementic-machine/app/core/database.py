from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.db = mongodb.client[settings.DATABASE_NAME]
        
        # Create indexes for better performance
        await mongodb.db.found_items.create_index([("item_id", ASCENDING)], unique=True)
        await mongodb.db.found_items.create_index([("category", ASCENDING)])
        await mongodb.db.found_items.create_index([("created_at", DESCENDING)])
        
        # Test connection
        await mongodb.client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.error(f"❌ Could not connect to MongoDB: {e}")
        logger.info("⚠️ Falling back to in-memory storage")

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")

def get_database():
    """Get database instance"""
    return mongodb.db
