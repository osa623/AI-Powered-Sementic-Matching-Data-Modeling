# Testing Guide - AI Semantic Matching System

## 🧪 How to Test the System

### Step 1: Add Found Items to Database
1. Go to **"Add Found Item"** tab
2. Add several wallets that people have found:

**Example Found Items:**
```
Category: Wallet
Description: Black leather wallet with national ID card and credit cards inside

Category: Wallet  
Description: Brown wallet ekak with blue ATM cards thiyanawa

Category: Wallet
Description: Small red purse with student ID and bus pass

Category: Wallet
Description: Dark brown leather wallet containing driver's license
```

### Step 2: Search for Lost Items
1. Go to **"Search My Lost Item"** tab
2. Describe your lost wallet (use different words):

**Example Lost Item Searches:**

#### Test 1: Similar Description (English)
```
Category: Wallet
Description: I lost a black wallet with ID cards
Expected: Should match "Black leather wallet with national ID card" with HIGH similarity (70-90%)
```

#### Test 2: Different Language (Singlish)
```
Category: Wallet
Description: mama rathu wallet ekak hoya giya with student card
Expected: Should match "Small red purse with student ID" with MEDIUM-HIGH similarity (60-85%)
```

#### Test 3: Semantic Similarity (Different Words)
```
Category: Wallet  
Description: Dark leather billfold with driver's permit
Expected: Should match "Dark brown leather wallet containing driver's license" with HIGH similarity (75-90%)
```

#### Test 4: Mixed Language
```
Category: Wallet
Description: Blue cards thiyana brown wallet ekak
Expected: Should match "Brown wallet ekak with blue ATM cards" with HIGH similarity (70-85%)
```

## 🎯 What to Observe

### Semantic Matching (Not Keyword)
- "wallet" matches "purse" ✅
- "ID card" matches "national ID card" ✅
- "rathu" (Sinhala for red) matches "red" ✅
- "driver's license" matches "driver's permit" ✅

### Similarity Scores
- **70-100%** (Green): Very likely match - same item
- **50-69%** (Orange): Possible match - similar items  
- **0-49%** (Gray): Low match - different items

### Multi-Language Support
- English: "black wallet with cards"
- Sinhala: "කළු පසුම්බිය cards සමඟ"
- Singlish: "mama black wallet ekak with cards hoya giya"
- All should match semantically!

## 🔬 Advanced Testing

### Test Case 1: Exact vs Semantic Match
**Found Item**: "Black leather wallet with driver's license"

**Lost Item A**: "Black leather wallet with driver's license"  
→ Should get ~95-100% (nearly identical)

**Lost Item B**: "Dark leather billfold with driving permit"  
→ Should get ~75-85% (semantic match with different words)

### Test Case 2: Cross-Language Matching
**Found Item**: "Red wallet with student cards"

**Lost Item**: "rathu wallet ekak with student ID"  
→ Should get ~70-85% (multilingual semantic match)

### Test Case 3: False Positives
**Found Item**: "Black leather wallet"

**Lost Item**: "Black leather jacket"  
→ Should get ~30-50% (low match - different category)

## 📊 Expected Results

### Good Matches (Should Rank High)
- Same item, different words
- Same language, synonyms
- Cross-language descriptions
- Different detail levels

### Poor Matches (Should Rank Low)  
- Different categories (wallet vs phone)
- Completely different items
- Opposite attributes (black vs white)

## 🐛 Troubleshooting

### If Similarity is Always Low (<50%)
- Check if items were actually added to database
- Verify the semantic model loaded correctly
- Check console for errors

### If Similarity is Too High (>90% for different items)
- This is expected for very generic descriptions
- Add more specific details to improve matching

### If No Results Appear
- Ensure category matches between found and lost items
- Check that items exist in database
- Verify backend is running on port 8000

## 💡 Pro Tips

1. **Add Specific Details**: "Black leather wallet with Visa card" is better than "wallet"
2. **Mix Languages**: The system supports English, Sinhala, and Singlish
3. **Use Natural Language**: Write like you're describing to a friend
4. **Check All Matches**: Even 50-60% matches might be relevant

## 🎬 Demo Script

```
1. Add 3-5 found wallets with varied descriptions
2. Wait 2 seconds (for indexing)
3. Search with similar but different words
4. Observe similarity percentages
5. Try different languages
6. Compare semantic vs keyword matching
```

## ✅ Success Criteria

- ✅ System understands semantic similarity (not just keywords)
- ✅ Works with multiple languages (English/Sinhala/Singlish)
- ✅ Shows percentage scores (0-100%)
- ✅ Ranks results by similarity
- ✅ "Black wallet" matches "dark purse" semantically
- ✅ Fast search (<1 second for 100s of items)
