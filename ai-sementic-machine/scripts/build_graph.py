import networkx as nx
import json
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY_PATH = os.path.join(BASE_DIR, '../data/raw/ontology_rules.json')
GRAPH_SAVE_PATH = os.path.join(BASE_DIR, '../data/models/knowledge_graph.pkl')

def build_knowledge_graph():
    print("Building Knowledge Graph...")
    G = nx.Graph()
    
    # Load ontology rules
    with open(ONTOLOGY_PATH, 'r', encoding='utf-8') as f:
        ontology = json.load(f)
    
    # Build graph from relationships
    for rule in ontology['relationships']:
        source = rule['source']
        for related in rule['related']:
            G.add_edge(source, related)
    
    # Save graph
    os.makedirs(os.path.dirname(GRAPH_SAVE_PATH), exist_ok=True)
    with open(GRAPH_SAVE_PATH, 'wb') as f:
        pickle.dump(G, f)
    
    print(f"✅ Knowledge Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    print(f"   Saved to: {GRAPH_SAVE_PATH}")

if __name__ == "__main__":
    build_knowledge_graph()
