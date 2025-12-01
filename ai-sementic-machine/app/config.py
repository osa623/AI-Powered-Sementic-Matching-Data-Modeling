import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("APP_NAME", "Semantic Engine")
    
    # Paths (Relative to project root)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "data/models/fine_tuned_bert")
    GRAPH_PATH = os.path.join(BASE_DIR, "data/models/knowledge_graph.pkl")
    INDEX_PATH = os.path.join(BASE_DIR, "data/indices/faiss.index")

settings = Settings()