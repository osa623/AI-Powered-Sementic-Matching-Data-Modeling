import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("APP_NAME", "Semantic Engine")
    
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "lost_and_found")
    
    # Paths (Relative to project root)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "data/models/fine_tuned_bert")
    GRAPH_PATH = os.path.join(BASE_DIR, "data/models/knowledge_graph.pkl")
    INDEX_PATH = os.path.join(BASE_DIR, "data/indices/faiss.index")
    METADATA_PATH = os.path.join(BASE_DIR, "data/indices/metadata.pkl")

settings = Settings()