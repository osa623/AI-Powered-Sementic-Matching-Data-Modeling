from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader
import json
import os
import random

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '../data/raw/text_pairs_english.json')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, '../data/models/fine_tuned_bert')

def train_model():
    print("=" * 70)
    print("🎓 ENGLISH-ONLY SEMANTIC FINE-TUNING FOR MAXIMUM ACCURACY")
    print("=" * 70)
    
    print("\n1️⃣ Loading Best English Model...")
    # Use the best English model
    try:
        model = SentenceTransformer('all-mpnet-base-v2')
        print("   ✅ Loaded all-mpnet-base-v2 (768-dim, Best for English)")
    except:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("   ✅ Loaded all-MiniLM-L6-v2 (384-dim, Fast & Accurate)")

    print("\n2️⃣ Loading English Training Data...")
    train_examples = []
    eval_examples = []
    
    # Create model directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        # Shuffle data for better train/eval split
        random.seed(42)
        random.shuffle(data)
        
        # Split 85% train, 15% eval
        split_idx = int(len(data) * 0.85)
        train_data = data[:split_idx]
        eval_data = data[split_idx:]
        
        print(f"   📊 Dataset: {len(train_data)} train, {len(eval_data)} eval")
        print(f"   📊 Total pairs: {len(data)}")
        
        # Prepare training examples with augmentation
        for item in train_data:
            # Original pair
            train_examples.append(InputExample(texts=[item['anchor'], item['positive']]))
            
            # Reversed pair (symmetric learning)
            train_examples.append(InputExample(texts=[item['positive'], item['anchor']]))
            
        # Prepare evaluation examples
        eval_sentences1 = []
        eval_sentences2 = []
        eval_scores = []
        
        for item in eval_data:
            eval_sentences1.append(item['anchor'])
            eval_sentences2.append(item['positive'])
            eval_scores.append(1.0)  # Positive pairs
    
    print(f"   ✅ {len(train_examples)} training examples (with augmentation)")
    print(f"   ✅ {len(eval_sentences1)} evaluation pairs")

    # 3. Create evaluator
    evaluator = EmbeddingSimilarityEvaluator(
        eval_sentences1, 
        eval_sentences2, 
        eval_scores,
        name='english_lost_found_eval'
    )

    # OPTIMIZED Training Configuration
    train_dataloader = DataLoader(
        train_examples, 
        shuffle=True, 
        batch_size=2  # Reduced to 2 for very long descriptions (200-300 words)
    )
    
    # MultipleNegativesRankingLoss - BEST for semantic search
    train_loss = losses.MultipleNegativesRankingLoss(model)
    
    # Training parameters - optimized for accuracy
    num_epochs = 20  # Extended training for better accuracy with detailed descriptions
    warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)
    
    print("\n3️⃣ Optimized Training Configuration:")
    print("   " + "-" * 60)
    print(f"   Base Model:        {type(model).__name__}")
    print(f"   Loss Function:     MultipleNegativesRankingLoss")
    print(f"   Batch Size:        2 (small for long descriptions)")
    print(f"   Epochs:            {num_epochs} (more for English-only)")
    print(f"   Warmup Steps:      {warmup_steps}")
    print(f"   Learning Rate:     2e-5")
    print(f"   Weight Decay:      0.01")
    print(f"   Evaluation:        Every epoch")
    print(f"   Best Model:        Auto-saved")
    print("   " + "-" * 60)
    
    print("\n4️⃣ Starting Fine-Tuning...")
    print("   Focus: English semantic understanding")
    print("   Goal: 95%+ accuracy on lost & found matching")
    print("   Time: ~10-15 minutes\n")
    
    # Train with best practices
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=num_epochs,
        warmup_steps=warmup_steps,
        evaluation_steps=len(train_dataloader),  # Evaluate after each epoch
        output_path=MODEL_SAVE_PATH,
        save_best_model=True,  # Save only the best model
        show_progress_bar=True,
        optimizer_params={'lr': 2e-5, 'weight_decay': 0.01}
    )

    print("\n" + "=" * 70)
    print("✅ ENGLISH FINE-TUNING COMPLETE!")
    print("=" * 70)
    
    print(f"\n📁 Fine-tuned model saved to: {MODEL_SAVE_PATH}")
    
    # Test the model
    print("\n5️⃣ Testing Fine-tuned Model...")
    test_queries = [
        ("Lost my black wallet", "Black leather wallet found"),
        ("Missing brown wallet with cards", "Brown wallet discovered with credit cards"),
        ("I lost my Samsung phone", "Samsung Galaxy smartphone found in canteen"),
        ("Keys with blue keychain lost", "Set of keys with blue keyring discovered"),
        ("Red backpack missing", "Red colored backpack found near cafeteria")
    ]
    
    print("\n   Similarity Scores (should be HIGH for matching pairs):")
    for query, target in test_queries:
        query_emb = model.encode(query, normalize_embeddings=True)
        target_emb = model.encode(target, normalize_embeddings=True)
        similarity = float(query_emb @ target_emb)  # Cosine similarity
        print(f"   • '{query[:30]}...' <=> '{target[:30]}...'")
        print(f"     Cosine Similarity: {similarity:.4f} ({similarity*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("📊 NEXT STEPS:")
    print("=" * 70)
    print("1. DELETE old index files:")
    print("   rm data/indices/faiss.index")
    print("   rm data/indices/metadata.pkl")
    print("")
    print("2. RESTART API server:")
    print("   uvicorn app.main:app --reload")
    print("")
    print("3. TEST with queries - expect 85-95% accuracy!")
    print("")
    print("4. For Singlish support: Add Singlish pairs and retrain")
    print("=" * 70)

if __name__ == "__main__":
    train_model()
