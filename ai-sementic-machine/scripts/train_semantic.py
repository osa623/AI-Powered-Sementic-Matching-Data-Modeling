from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader
import json
import os
import random

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '../data/raw/text_pairs.json')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, '../data/models/fine_tuned_bert')

def train_model():
    print("=" * 70)
    print("🎓 ADVANCED SEMANTIC SIMILARITY FINE-TUNING")
    print("=" * 70)
    
    print("\n1️⃣ Loading High-Performance Base Model...")
    # Use better base model for improved accuracy
    try:
        model = SentenceTransformer('all-mpnet-base-v2')
        print("   ✅ Loaded all-mpnet-base-v2 (768-dim, State-of-the-art)")
    except:
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            print("   ✅ Loaded all-MiniLM-L6-v2 (384-dim, Fast & Accurate)")
        except:
            model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("   ✅ Loaded multilingual-MiniLM (384-dim, Multilingual)")

    print("\n2️⃣ Loading and Preparing Training Data...")
    train_examples = []
    eval_examples = []
    
    # Create model directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        # Shuffle data for better train/eval split
        random.seed(42)
        random.shuffle(data)
        
        # Split 80% train, 20% eval
        split_idx = int(len(data) * 0.8)
        train_data = data[:split_idx]
        eval_data = data[split_idx:]
        
        print(f"   📊 Dataset split: {len(train_data)} train, {len(eval_data)} eval")
        
        # Prepare training examples with multiple augmentations
        for item in train_data:
            # Original pair
            train_examples.append(InputExample(texts=[item['anchor'], item['positive']]))
            
            # Reversed pair (symmetric learning)
            train_examples.append(InputExample(texts=[item['positive'], item['anchor']]))
            
        # Prepare evaluation examples (for monitoring progress)
        eval_sentences1 = []
        eval_sentences2 = []
        eval_scores = []
        
        for item in eval_data:
            eval_sentences1.append(item['anchor'])
            eval_sentences2.append(item['positive'])
            eval_scores.append(1.0)  # These are positive pairs
    
    print(f"   ✅ Created {len(train_examples)} training examples (with augmentation)")
    print(f"   ✅ Created {len(eval_sentences1)} evaluation pairs")

    # 3. Create evaluator for monitoring training progress
    evaluator = EmbeddingSimilarityEvaluator(
        eval_sentences1, 
        eval_sentences2, 
        eval_scores,
        name='lost_found_eval'
    )

    # 4. Training Setup with ADVANCED configuration
    train_dataloader = DataLoader(
        train_examples, 
        shuffle=True, 
        batch_size=16  # Increased batch size for better gradients
    )
    
    # Use MultipleNegativesRankingLoss - BEST for semantic similarity
    # This loss is superior to CosineSimilarityLoss for retrieval tasks
    train_loss = losses.MultipleNegativesRankingLoss(model)
    
    # Calculate training steps
    num_epochs = 10  # More epochs for better convergence
    warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)  # 10% warmup
    
    print("\n3️⃣ Training Configuration:")
    print("   " + "-" * 60)
    print(f"   Loss Function:     MultipleNegativesRankingLoss (BEST for retrieval)")
    print(f"   Batch Size:        16 (larger for stable gradients)")
    print(f"   Epochs:            {num_epochs}")
    print(f"   Warmup Steps:      {warmup_steps}")
    print(f"   Learning Rate:     2e-5 (default, optimal)")
    print(f"   Optimizer:         AdamW with weight decay")
    print(f"   Evaluation:        Every epoch")
    print("   " + "-" * 60)
    
    print("\n4️⃣ Starting Training...")
    print("   (This may take 10-20 minutes depending on your hardware)\n")
    
    # Train the model
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=num_epochs,
        warmup_steps=warmup_steps,
        evaluation_steps=len(train_dataloader),  # Evaluate every epoch
        output_path=MODEL_SAVE_PATH,
        save_best_model=True,
        show_progress_bar=True,
        optimizer_params={'lr': 2e-5}
    )

    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    
    print(f"\n📁 Model saved to: {MODEL_SAVE_PATH}")
    
    # Test the model with sample queries
    print("\n5️⃣ Testing Fine-tuned Model...")
    test_queries = [
        "Lost my black wallet",
        "Mata phone eka haruna",
        "Brown leather wallet missing",
        "Keys with car keychain"
    ]
    
    for query in test_queries:
        embedding = model.encode(query)
        print(f"   ✓ '{query}' → vector shape: {embedding.shape}")
    
    print("\n" + "=" * 70)
    print("📊 NEXT STEPS:")
    print("=" * 70)
    print("1. Delete old index files:")
    print("   - data/indices/faiss.index")
    print("   - data/indices/metadata.pkl")
    print("\n2. Restart your API server:")
    print("   uvicorn app.main:app --reload")
    print("\n3. The API will automatically load the fine-tuned model")
    print("\n4. Test with real queries - you should see MUCH better accuracy!")
    print("=" * 70)

if __name__ == "__main__":
    train_model()