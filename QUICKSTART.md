# Feature 4 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)

```bash
cd "d:\stemlink recourses\IKMS Multi-Agent RAG\class-12"
pip install -r requirements.txt
```

### Step 2: Set Environment Variables (1 min)

Create `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=ikms-vectors
PINECONE_ENVIRONMENT=us-west-2
```

### Step 3: Start Backend (1 min)

```bash
uvicorn src.app.api:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Open Frontend (1 min)

Open in your browser:
```
file:///d:/stemlink%20recourses/IKMS%20Multi-Agent%20RAG/class-12/index.html
```

Or if using a local server:
```bash
# In another terminal
python -m http.server 8080
# Then open: http://localhost:8080
```

### Step 5: Test the System

Type a question in the frontend:
```
"What is HNSW indexing?"
```

You should see:
1. ✅ Answer with inline citations like `[C1]`, `[C2]`
2. ✅ Source Materials panel showing all citations
3. ✅ Click citations to highlight sources
4. ✅ Statistics showing citations found

## How It Works

### Behind the Scenes

```
Your Question
    ↓
Retrieval Agent (fetches relevant chunks, generates C1, C2, C3 IDs)
    ↓
Summarization Agent (generates answer with citations: "... [C1] ... [C2] ...")
    ↓
Verification Agent (checks accuracy, maintains citations)
    ↓
Frontend (displays answer + clickable citations + source panel)
```

### What's New in Feature 4

| Before | After |
|--------|-------|
| "HNSW provides fast search." | "HNSW provides fast search [C1][C2]." |
| No source traceability | Click [C1] → See source on page 5 |
| Black box | Transparent evidence-backed answers |

## Testing Checklist

- [ ] **Backend Running**: http://localhost:8000 responds
- [ ] **Frontend Loads**: index.html displays UI
- [ ] **Question Works**: Type question, get answer
- [ ] **Citations Display**: Answer includes [C#] citations
- [ ] **Source Panel**: Shows all citations with metadata
- [ ] **Click Citations**: Clicking [C1] highlights source
- [ ] **API Response**: Includes citations dict with page/source info

## Common Questions

### Q: Why are there no citations?

**A**: Check the answer contains [C#] patterns. If not:
1. Verify OpenAI API key is correct
2. Ensure Pinecone index is indexed with data
3. Check agent prompt was updated (see FEATURE_4_README.md)

### Q: Why is it slow?

**A**: First request takes time for:
- Model initialization (~2-3 sec)
- Retrieval from Pinecone (~1-2 sec)
- LLM inference for 3 agents (~3-5 sec)

Subsequent requests are slightly faster.

### Q: Can I change the number of citations?

**A**: Yes, modify retrieval parameters in `src/app/core/tools.py`:

```python
@tool(response_format="content_and_artifact")
def retrieval_tool(query: str):
    docs = retrieve(query, k=4)  # Change k to 6 or 8 for more citations
```

### Q: How do I add more PDF documents?

**A**: Use the `/index-pdf` endpoint:

```bash
curl -X POST http://localhost:8000/index-pdf \
  -F "file=@document.pdf"
```

Or create a simple web form in the frontend.

## File Structure

```
class-12/
├── index.html                    ← Frontend UI (NEW)
├── FEATURE_4_README.md          ← Feature documentation (NEW)
├── DEPLOYMENT_GUIDE.md          ← Deployment instructions (NEW)
├── test_feature_4.py            ← Test validation script (NEW)
├── .env                         ← Your API keys (create this)
├── requirements.txt
├── src/
│   └── app/
│       ├── api.py               ← UPDATED: Returns citations
│       ├── models.py            ← UPDATED: QAResponse with citations
│       └── core/
│           ├── agents/
│           │   ├── agents.py    ← UPDATED: Citation extraction
│           │   ├── prompts.py   ← UPDATED: Citation instructions
│           │   ├── state.py     ← UPDATED: Citations field
│           │   └── ...
│           └── retrieval/
│               └── serialization.py  ← UPDATED: Citation ID generation
└── ...
```

## Understanding the Code Changes

### 1. State Schema (3 lines changed)
```python
# NEW fields added to QAState
citations: dict[str, dict] | None
raw_docs: list | None
```

### 2. Citation ID Generation (40 lines new function)
```python
# NEW function in serialization.py
def serialize_chunks_with_citations(docs):
    # Generates C1, C2, C3 IDs and citation metadata
```

### 3. Agent Prompts (15 lines added)
```python
# Updated SUMMARIZATION_SYSTEM_PROMPT with:
# "Include citation IDs [C1], [C2] after statements"

# Updated VERIFICATION_SYSTEM_PROMPT with:
# "Maintain citation integrity while verifying"
```

### 4. Retrieval Node (20 lines modified)
```python
# Changed: Also extract citation mapping
context, citations = serialize_chunks_with_citations(raw_docs)
```

### 5. API Response (1 line changed)
```python
# NEW: Return citations dict to frontend
return QAResponse(..., citations=result.get("citations"))
```

## Next Steps

### To Deepen Your Learning

1. **Study LangGraph**: Trace how state flows through nodes
2. **Experiment with Prompts**: Modify agent prompts in `prompts.py`
3. **Enhance UI**: Add features to `index.html`:
   - Toggle full/snippet content
   - Export answer as PDF
   - Citation search
   - Confidence scores
4. **Improve Retrieval**: Experiment with different `k` values
5. **Add Features**: Implement Feature 1, 2, 3, or 5

### Advanced Modifications

**Add Confidence Scoring**:
```python
# In verification_node, add confidence score
confidence = estimate_confidence(answer, context)
return {"answer": answer, "confidence": confidence}
```

**Multi-turn Conversations** (Feature 5):
```python
# Modify state to track history
history: list[dict] | None
# Then build session management in API
```

**Context Criticism** (Feature 3):
```python
# Add new node: context_critic_node
# Filter low-relevance chunks before summarization
```

## Testing Advanced Scenarios

### Test 1: Complex Multi-Part Question
```
"What are the advantages of HNSW compared to LSH, 
and how does IVF improve scalability?"
```
Expected: Multiple citations [C1][C2][C3][C4]

### Test 2: Comparison Questions
```
"Compare vector databases and traditional databases"
```
Expected: Citations from both topics

### Test 3: Technical Details
```
"Explain the mathematical basis of similarity search"
```
Expected: Well-cited technical answer

## Troubleshooting Reference

| Issue | Cause | Solution |
|-------|-------|----------|
| No citations in answer | Model not following instructions | Check SUMMARIZATION prompt |
| Missing sources in panel | Citation extraction failed | Check retrieval_tool artifact |
| CORS error in frontend | Backend CORS not configured | Already added in code |
| Slow response | Model latency | Check OpenAI API status |
| Pinecone errors | Index not found or not indexed | Create index and run indexing |

## Performance Expectations

| Metric | Expected Time |
|--------|-------|
| First request | 8-12 seconds |
| Subsequent requests | 5-8 seconds |
| Frontend response | <100ms |
| Citation extraction | <200ms |

(Times depend on model, network, Pinecone latency)

## Resources

- [Feature 4 README](FEATURE_4_README.md) - Detailed implementation
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production setup
- [Test Script](test_feature_4.py) - Validation
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/) - Graph framework
- [OpenAI API Docs](https://platform.openai.com/docs/) - LLM integration

## Success Criteria

You've successfully implemented Feature 4 when:

✅ Backend runs without errors
✅ Frontend displays UI
✅ Answers include inline citations [C#]
✅ Citations panel shows metadata
✅ Clicking citations highlights sources
✅ API response includes citations dict
✅ All tests pass (run test_feature_4.py)

## Questions?

Review these in order:
1. FEATURE_4_README.md (detailed explanation)
2. Code comments (in modified files)
3. test_feature_4.py (how validation works)
4. DEPLOYMENT_GUIDE.md (production checklist)

Good luck! 🚀
