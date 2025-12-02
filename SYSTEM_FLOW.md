# AI-Powered Semantic Machine - System Flow

## 🎯 Purpose
This system uses **AI-powered semantic vector matching** (not keyword matching) to help people find their lost items by matching them against found items in the database.

## 🔄 How It Works

### Phase 1: Adding Found Items to Database
1. Someone finds a wallet (or other item)
2. They describe it in the system: "Black leather wallet with ID cards"
3. The system:
   - Converts description to a 384-dimensional vector using multilingual transformer model
   - Stores the vector in FAISS index (Facebook AI Similarity Search)
   - Saves metadata (ID, description, category)
   - **Item is now searchable in the database**

### Phase 2: Searching for Lost Items
1. Owner realizes they lost their wallet
2. They describe it: "Brown wallet with blue cards" or "mama rathu wallet ekak hoya giya"
3. The system:
   - Converts their description to a vector
   - Searches FAISS index for similar vectors (semantic similarity, not keyword matching)
   - Calculates similarity percentage (0-100%)
   - Returns all matching found items ranked by similarity

## 🤖 AI Technology Used

### Semantic Matching Engine
- **Model**: `paraphrase-multilingual-MiniLM-L12-v2` (Sentence Transformers)
- **Vector Dimension**: 384
- **Languages Supported**: English, Sinhala, Singlish (code-mixed)
- **Similarity Metric**: L2 Distance converted to percentage

### Why Semantic (Not Keyword)?
**Traditional Keyword Matching:**
- "black leather wallet" ≠ "dark leather purse" ❌
- Requires exact word matches

**Semantic Vector Matching:**
- "black leather wallet" ≈ "dark leather purse" ✅ (85% similar)
- "mama wallet eka hoya giya" ≈ "I lost my wallet" ✅ (78% similar)
- Understands **meaning**, not just words

## 📊 Similarity Scoring

- **70-100%**: High match (Green) - Very likely the same item
- **50-69%**: Medium match (Orange) - Possibly the same item
- **0-49%**: Low match (Gray) - Different but related items

## 🔧 Technical Stack

### Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **AI Model**: Sentence Transformers
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Data Processing**: NumPy, Pandas

### Frontend (React)
- **Framework**: React 19.2.0
- **HTTP Client**: Axios
- **Styling**: Custom CSS with gradients

## 📡 API Endpoints

### 1. Add Found Item
```
POST /index
Body: {
  "id": "FOUND-123456789",
  "description": "Black leather wallet with ID cards",
  "category": "Wallet"
}
```

### 2. Search Lost Item
```
POST /search
Body: {
  "text": "Brown wallet with blue cards",
  "category": "Wallet",
  "limit": 10
}
Response: {
  "matches": [
    {
      "id": "FOUND-123456789",
      "description": "Black leather wallet with ID cards",
      "category": "Wallet",
      "score": 85.67,
      "reason": "AI Semantic Vector Similarity"
    }
  ],
  "total_matches": 1
}
```

## 🚀 Running the System

### Backend (Port 8000)
```bash
cd ai-sementic-machine
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Port 3001)
```bash
cd frontendsample
npm start
```

### Access
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🎯 User Journey

1. **Found Item Scenario**:
   - Person A finds a wallet → Adds to system with description
   - Vector stored in database

2. **Lost Item Scenario**:
   - Person B (owner) lost wallet → Searches with description
   - System matches against all found items using AI
   - Shows similarity percentages
   - Person B can identify their item from matches

## 🔐 Data Privacy
- Only descriptions, categories, and generated IDs are stored
- No personal information is required
- Vectors are mathematical representations, not readable text
