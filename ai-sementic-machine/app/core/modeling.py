import networkx as nx
import pickle
import os
from app.config import settings

class DataModelingEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataModelingEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("Loading Knowledge Graph...")
        if os.path.exists(settings.GRAPH_PATH):
            with open(settings.GRAPH_PATH, 'rb') as f:
                self.graph = pickle.load(f)
            print("✅ Knowledge Graph Loaded.")
        else:
            print("⚠️ Graph not found. Initializing empty graph.")
            self.graph = nx.Graph()

    def get_context(self, category: str):
        """
        Returns related categories based on the data model.
        E.g., Input: 'Wallet' -> Output: ['ID Card', 'Cash', 'Credit Card']
        """
        try:
            # Get neighbors (related items)
            related = list(self.graph.neighbors(category))
            return related
        except Exception:
            return []