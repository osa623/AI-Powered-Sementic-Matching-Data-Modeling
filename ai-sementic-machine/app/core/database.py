from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    _connected: bool = False

mongodb = MongoDB()

async def connect_to_mongo(max_retries: int = 3, retry_delay: int = 2) -> bool:
    """Connect to MongoDB on startup with retry logic
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting MongoDB connection (attempt {attempt}/{max_retries})...")
            
            # Create client with timeout
            mongodb.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000
            )
            mongodb.db = mongodb.client[settings.DATABASE_NAME]
            
            # Test connection with ping - THIS IS CRITICAL
            await mongodb.client.admin.command('ping')
            logger.info("✅ MongoDB ping successful")
            
            # Create indexes for better performance
            await mongodb.db.found_items.create_index([("item_id", ASCENDING)], unique=True)
            await mongodb.db.found_items.create_index([("category", ASCENDING)])
            await mongodb.db.found_items.create_index([("created_at", DESCENDING)])
            logger.info("✅ Database indexes created")
            
            mongodb._connected = True
            logger.info(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("❌ All MongoDB connection attempts failed")
                logger.info("⚠️ System will run in standalone mode with disk cache")
                mongodb._connected = False
                return False
    
    return False

def is_mongodb_connected() -> bool:
    """Check if MongoDB is connected and ready"""
    return mongodb._connected and mongodb.client is not None and mongodb.db is not None

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")

def get_database():
    """Get database instance
    
    Returns:
        Database instance if connected, None otherwise
    """
    if is_mongodb_connected():
        return mongodb.db
    return None
