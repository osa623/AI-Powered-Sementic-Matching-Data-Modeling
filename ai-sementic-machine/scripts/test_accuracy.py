"""
Test script to validate semantic matching accuracy improvements
Run this after implementing the changes to see the improvement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.semantic import SemanticEngine
import asyncio
import numpy as np

def print_separator(char="=", length=60):
    print(char * length)

async def test_accuracy():
    print_separator()
    print("🧪 SEMANTIC MATCHING ACCURACY TEST")
    print_separator()
    
    # Initialize engine
    print("\n1️⃣ Initializing Semantic Engine...")
    engine = SemanticEngine()
    print(f"   Model: {engine.model}")
    print(f"   Dimension: {engine.dimension}")
    print(f"   Index Type: {type(engine.index).__name__}")
    
    # Test data
    print("\n2️⃣ Adding Test Items...")
    test_items = [
        {"id": "W001", "description": "Black leather wallet with cards", "category": "Wallet"},
        {"id": "W002", "description": "Brown wallet found in parking lot", "category": "Wallet"},
        {"id": "P001", "description": "iPhone 12 mobile phone", "category": "Electronics"},
        {"id": "P002", "description": "Samsung Galaxy smartphone", "category": "Electronics"},
        {"id": "U001", "description": "Red folding umbrella", "category": "Accessories"},
        {"id": "U002", "description": "Blue large umbrella with handle", "category": "Accessories"},
        {"id": "B001", "description": "Black laptop backpack with straps", "category": "Bag"},
        {"id": "K001", "description": "Car keys with Toyota keychain", "category": "Keys"},
        {"id": "G001", "description": "Black frame reading glasses", "category": "Accessories"},
        {"id": "C001", "description": "Dell laptop charger 65W", "category": "Electronics"}
    ]
    
    for item in test_items:
        await engine.add_item(item)
    
    print(f"   ✅ Added {len(test_items)} test items")
    
    # Test queries
    print("\n3️⃣ Running Test Queries...")
    print_separator("-")
    
    test_queries = [
        {
            "query": "Lost my black wallet",
            "expected_category": "Wallet",
            "expected_top": "W001"
        },
        {
            "query": "Mata phone eka haruna",
            "expected_category": "Electronics",
            "expected_top": "P001"
        },
        {
            "query": "Rathu pata umbrella",
            "expected_category": "Accessories",
            "expected_top": "U001"
        },
        {
            "query": "Lost my laptop charger",
            "expected_category": "Electronics",
            "expected_top": "C001"
        },
        {
            "query": "Keys with car keychain",
            "expected_category": "Keys",
            "expected_top": "K001"
        }
    ]
    
    correct_predictions = 0
    total_queries = len(test_queries)
    
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected_id = test["expected_top"]
        
        results = engine.search(query, limit=3)
        
        print(f"\n📝 Test {i}/{total_queries}: \"{query}\"")
        print(f"   Expected: {expected_id}")
        
        if results and len(results) > 0:
            top_result = results[0]
            top_id = top_result['item']['id']
            
            print(f"   Got: {top_id} ({top_result['item']['description']})")
            print(f"   📊 Scores:")
            print(f"      • Final Score: {top_result['semantic_score']}%")
            print(f"      • Semantic: {top_result['details']['semantic']}%")
            print(f"      • Keyword: {top_result['details']['keyword']}%")
            print(f"      • Cosine Sim: {top_result['cosine_similarity']}")
            
            if top_id == expected_id:
                print(f"   ✅ CORRECT!")
                correct_predictions += 1
            else:
                print(f"   ❌ WRONG (Expected {expected_id})")
                
            # Show top 3
            print(f"\n   Top 3 Matches:")
            for j, r in enumerate(results[:3], 1):
                print(f"      {j}. {r['item']['id']}: {r['semantic_score']}% - {r['item']['description']}")
        else:
            print(f"   ❌ NO RESULTS")
        
        print_separator("-")
    
    # Calculate accuracy
    accuracy = (correct_predictions / total_queries) * 100
    
    print("\n4️⃣ RESULTS SUMMARY")
    print_separator("=")
    print(f"   Correct Predictions: {correct_predictions}/{total_queries}")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   Status: {'✅ EXCELLENT' if accuracy >= 80 else '⚠️ NEEDS IMPROVEMENT' if accuracy >= 60 else '❌ POOR'}")
    print_separator("=")
    
    # Performance benchmark
    print("\n5️⃣ Performance Benchmark...")
    import time
    
    start_time = time.time()
    for _ in range(100):
        engine.search("test query", limit=10)
    end_time = time.time()
    
    avg_time_ms = ((end_time - start_time) / 100) * 1000
    print(f"   Average search time: {avg_time_ms:.2f}ms")
    print(f"   Throughput: {1000/avg_time_ms:.0f} queries/second")
    
    # Model info
    print("\n6️⃣ Model Information")
    print(f"   Model Type: {type(engine.model).__name__}")
    print(f"   Embedding Dimension: {engine.dimension}")
    print(f"   Total Items Indexed: {len(engine.items_metadata)}")
    print(f"   Index Type: {type(engine.index).__name__}")
    
    print("\n✨ Test Complete!")
    print_separator("=")

if __name__ == "__main__":
    asyncio.run(test_accuracy())
