from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import json
import os

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '../data/raw/text_pairs.json')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, '../data/models/fine_tuned_bert')

def train_model():
    print("1. Loading Base Model (MiniLM)...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    print("2. Loading Data...")
    train_examples = []
    
    # Create model directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            train_examples.append(InputExample(texts=[item['anchor'], item['positive']]))

    print(f"   Loaded {len(train_examples)} training pairs.")

    # 3. Training Setup
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=2) # Small batch for testing
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # 4. Train
    print("3. Starting Training (This may take a moment)...")
    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=3)

    # 5. Save
    model.save(MODEL_SAVE_PATH)
    print(f"✅ Success! Model saved to: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_model()