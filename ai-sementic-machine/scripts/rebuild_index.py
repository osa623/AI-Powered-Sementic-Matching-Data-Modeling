"""
Utility script to rebuild FAISS index with improved settings
Run this after updating to cosine similarity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.semantic import SemanticEngine
from app.core.database import get_database
import asyncio

async def rebuild_index():
    print("=" * 60)
    print("🔨 REBUILDING SEMANTIC INDEX")
    print("=" * 60)
    
    # Step 1: Remove old index files
    print("\n1️⃣ Cleaning old index files...")
    from app.config import settings
    
    index_path = settings.INDEX_PATH
    metadata_path = settings.METADATA_PATH
    
    if os.path.exists(index_path):
        os.remove(index_path)
        print(f"   ✅ Removed old index: {index_path}")
    else:
        print(f"   ℹ️ No old index found")
    
    if os.path.exists(metadata_path):
        os.remove(metadata_path)
        print(f"   ✅ Removed old metadata: {metadata_path}")
    else:
        print(f"   ℹ️ No old metadata found")
    
    # Step 2: Initialize new engine
    print("\n2️⃣ Initializing new Semantic Engine...")
    engine = SemanticEngine()
    print(f"   Model: {type(engine.model).__name__}")
    print(f"   Dimension: {engine.dimension}")
    print(f"   Index Type: {type(engine.index).__name__}")
    
    # Step 3: Load from MongoDB
    print("\n3️⃣ Loading items from MongoDB...")
    try:
        await engine.load_from_mongodb()
        print(f"   ✅ Successfully loaded items")
        print(f"   Total items in index: {len(engine.items_metadata)}")
    except Exception as e:
        print(f"   ⚠️ Could not load from MongoDB: {e}")
        print(f"   Index will be empty until items are added via API")
    
    # Step 4: Verify index
    print("\n4️⃣ Verifying index integrity...")
    print(f"   FAISS index size: {engine.index.ntotal}")
    print(f"   Metadata size: {len(engine.items_metadata)}")
    
    if engine.index.ntotal == len(engine.items_metadata):
        print(f"   ✅ Index and metadata are in sync")
    else:
        print(f"   ⚠️ Mismatch detected!")
    
    # Step 5: Test search
    if len(engine.items_metadata) > 0:
        print("\n5️⃣ Testing search functionality...")
        test_query = "test item"
        results = engine.search(test_query, limit=3)
        
        if results:
            print(f"   ✅ Search working! Found {len(results)} results")
            print(f"   Top result score: {results[0]['semantic_score']}%")
        else:
            print(f"   ⚠️ No results found")
    else:
        print("\n5️⃣ Skipping search test (no items in index)")
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ REBUILD COMPLETE!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Restart your API server")
    print("   2. Add items using POST /index endpoint")
    print("   3. Test searches using POST /search endpoint")
    print("   4. Run test_accuracy.py to validate improvements")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(rebuild_index())
