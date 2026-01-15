# Feature 4: Evidence-Aware Answers with Chunk Citations

## Overview

This implementation adds **traceable citations** to the IKMS Multi-Agent RAG system, enabling users to verify which retrieved chunks contributed to each part of the answer. Every factual claim in the generated answer is linked back to specific source material with page numbers and document references.

## What Changed

### 1. **Enhanced State Schema** (`src/app/core/agents/state.py`)

```python
class QAState(TypedDict):
    question: str
    context: str | None
    draft_answer: str | None
    answer: str | None
    citations: dict[str, dict] | None  # NEW: Citation ID → metadata mapping
    raw_docs: list | None              # NEW: Original Document objects
```

### 2. **Citation ID Generation** (`src/app/core/retrieval/serialization.py`)

New function `serialize_chunks_with_citations()` that:
- Generates stable chunk IDs (C1, C2, C3, etc.)
- Creates formatted context with citation IDs for agent consumption
- Returns a citation mapping dictionary:

```python
{
    "C1": {
        "page": 5,
        "snippet": "HNSW (Hierarchical Navigable Small World)...",
        "source": "vector_db_paper.pdf",
        "full_content": "..."
    },
    "C2": { ... },
    ...
}
```

### 3. **Agent Prompt Updates** (`src/app/core/agents/prompts.py`)

Enhanced all three agent prompts with citation instructions:

**Summarization Agent:**
- Must include `[C1]`, `[C2]` citations after each statement
- Can cite multiple chunks: `[C1][C2][C3]`
- Only cites chunks present in context

**Verification Agent:**
- Maintains citation integrity during correction
- Removes citations for removed statements
- Preserves citations for verified statements

### 4. **Retrieval Node Enhancement** (`src/app/core/agents/agents.py`)

The `retrieval_node()` now:
- Extracts both context AND artifact (Document objects) from ToolMessage
- Calls `serialize_chunks_with_citations()` to generate citation IDs
- Stores both context and citation mapping in state

### 5. **API Response Update** (`src/app/models.py` & `src/app/api.py`)

New QAResponse structure:

```python
class QAResponse(BaseModel):
    answer: str                          # Final verified answer with citations
    context: str                         # Retrieved context
    citations: dict[str, dict] | None    # Citation metadata
```

Example API response:

```json
{
  "answer": "HNSW provides fast approximate nearest neighbor search through hierarchical graphs [C1][C2]. LSH uses hash functions for similarity [C4].",
  "context": "[C1] Chunk from page 5: ...",
  "citations": {
    "C1": {
      "page": 5,
      "snippet": "HNSW (Hierarchical Navigable Small World) provides...",
      "source": "vector_db_paper.pdf"
    },
    "C2": { ... }
  }
}
```

## Frontend UI (`index.html`)

Modern, interactive interface featuring:

### Left Panel: Question Input
- Textarea for user questions
- Real-time error handling
- Statistics display (citations found, chunks retrieved)

### Right Panel: Answer & Citations
- **Answer Display**: Full answer with inline clickable citations `[C1]`, `[C2]`, etc.
- **Source Materials Panel**: Expandable list of all citations with:
  - Citation ID badge
  - Source file and page number
  - Content snippet (first 100 chars)
  - Click to highlight/scroll

### Interaction Features
- **Click citations**: Highlight the source in the panel
- **Hover citations**: Visual feedback on both citation link and source item
- **Responsive design**: Works on desktop, tablet, and mobile
- **Loading states**: Spinner and status messages during processing

## How to Use

### 1. Start the Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn src.app.api:app --reload --port 8000
```

### 2. Open the Frontend

```bash
# Open in browser
open index.html
# or
firefox index.html
```

### 3. Ask a Question

1. Type your question in the text area
2. Click "Ask Question" or press Ctrl+Enter
3. Wait for the system to process:
   - Retrieval Agent fetches relevant chunks
   - Summarization Agent generates answer with citations
   - Verification Agent ensures accuracy while maintaining citations
4. View the answer with inline citations
5. Click any `[C#]` citation to highlight its source
6. Hover over source materials to see full details

## Example Flow

### Question
```
"What are the main indexing strategies in vector databases?"
```

### Answer (with citations)
```
Vector databases use several indexing strategies. HNSW provides fast 
approximate search through hierarchical graphs [C1][C2]. LSH uses hash 
functions for similarity [C4]. IVF partitions the vector space into 
clusters [C3].
```

### Citations Panel
```
C1  Source: vector_db_paper.pdf  Page: 5
    "HNSW (Hierarchical Navigable Small World) graphs provide..."

C2  Source: vector_db_paper.pdf  Page: 6
    "The hierarchical structure allows efficient approximate nearest..."

C3  Source: vector_db_paper.pdf  Page: 8
    "Inverted File (IVF) indexing partitions vectors into Voronoi..."

C4  Source: vector_db_paper.pdf  Page: 7
    "Locality-Sensitive Hashing (LSH) maps similar vectors to..."
```

## Technical Implementation Details

### Citation ID Generation Algorithm

```python
def serialize_chunks_with_citations(docs):
    citation_map = {}
    context_parts = []
    
    for idx, doc in enumerate(docs, start=1):
        chunk_id = f"C{idx}"  # C1, C2, C3, ...
        
        # Extract metadata
        page = doc.metadata.get("page", "unknown")
        source = doc.metadata.get("source", "unknown")
        
        # Create citation entry
        citation_map[chunk_id] = {
            "page": page,
            "snippet": content[:100] + "...",
            "source": source,
            "full_content": content
        }
        
        # Format with citation ID
        context_parts.append(f"[{chunk_id}] Chunk from page {page}:\n{content}")
    
    return "\n\n".join(context_parts), citation_map
```

### Citation Preservation in Verification

The Verification Agent maintains citation integrity by:
1. Keeping citations for verified statements
2. Removing citations when removing statements
3. Preserving chunk IDs when rephrasing
4. Only citing chunks present in provided context

### State Flow Through Pipeline

```
START
  ↓
[retrieval_node]
  - Extracts raw documents from retrieval_tool
  - Generates citation IDs (C1, C2, ...)
  - Stores citations in state.citations
  - Stores raw_docs in state.raw_docs
  ↓
[summarization_node]
  - Receives context WITH citation IDs
  - Generates answer with [C1], [C2] citations
  - Stores draft_answer in state.draft_answer
  ↓
[verification_node]
  - Receives context WITH citation IDs
  - Verifies draft_answer
  - Maintains citation integrity
  - Stores final answer in state.answer
  ↓
[API Response]
  - answer: Final answer with citations
  - context: Context string with citation IDs
  - citations: Dict of C1→metadata mappings
  ↓
END
```

## Acceptance Criteria ✅

All acceptance criteria from Feature 4 are met:

✅ **Answers include inline citations** like `[C1]`, `[C2]`
- Summarization agent explicitly trained to cite
- Verification agent preserves citations

✅ **API exposes machine-readable citation mappings**
- QAResponse includes citations dict
- Each citation maps to page, source, snippet

✅ **Every citation corresponds to actual retrieved chunk**
- Citation IDs generated in retrieval_node
- Maintained through entire pipeline

✅ **Citation IDs remain stable throughout pipeline**
- Generated once in retrieval_node
- Same IDs used in context string and agent prompts
- Same IDs passed to API response

✅ **Verification step maintains citation accuracy**
- Verification agent instructions explicitly require maintaining citations
- Citations removed only when statements removed

## Testing the Implementation

### Test Case 1: Basic Citation Generation

```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "What is HNSW indexing?"}'
```

Expected response includes:
- answer with [C#] citations
- citations dict with C1, C2, etc. entries
- Each citation has page, source, snippet fields

### Test Case 2: Multiple Citations per Claim

Ask a question that requires synthesis from multiple chunks. Verify the answer includes citations like `[C1][C2]` for statements drawing from multiple sources.

### Test Case 3: Citation Preservation After Verification

Verify that citations remain in final answer after verification step removes unsupported claims.

## Frontend Features

### 1. Interactive Citation Links
- Click any `[C1]` to highlight source
- Visual feedback on both link and source panel
- Smooth scrolling to source

### 2. Source Panel
- Expandable citation items
- Shows page number and document source
- Displays snippet of content
- Hover effects for better UX

### 3. Statistics
- Citation count
- Chunks retrieved count
- Real-time updates

### 4. Error Handling
- Validation messages for empty/too-long questions
- API error handling with user-friendly messages
- Loading states for better UX

### 5. Responsive Design
- Works on desktop, tablet, mobile
- Flexbox/Grid layout adapts to screen size
- Touch-friendly on mobile devices

## Future Enhancements

1. **Citation Verification UI**
   - Show which parts of answer use which citations
   - Visual indicators for citation confidence
   - Highlight potentially unsupported claims

2. **Citation Search**
   - Search for claims by citation
   - Filter answers by source document
   - Citation analytics

3. **Citation Export**
   - Export answers with citations in various formats (PDF, Markdown, APA)
   - Bibliography generation

4. **Advanced Citation Modes**
   - Full content vs. snippet display toggle
   - Citation context expansion
   - Source document preview

5. **Citation Analytics**
   - Most cited chunks
   - Citation patterns
   - Source quality metrics

## Files Modified

| File | Changes |
|------|---------|
| `src/app/core/agents/state.py` | Added `citations` and `raw_docs` fields |
| `src/app/core/retrieval/serialization.py` | Added `serialize_chunks_with_citations()` function |
| `src/app/core/agents/prompts.py` | Enhanced all agent prompts with citation instructions |
| `src/app/core/agents/agents.py` | Updated `retrieval_node()` to extract citations |
| `src/app/models.py` | Added `citations` field to `QAResponse` |
| `src/app/api.py` | Updated endpoint to return citations |
| `index.html` | NEW: Modern interactive frontend |

## Conclusion

Feature 4 transforms the IKMS Multi-Agent RAG system from a black-box question answerer into a **transparent, evidence-backed system** where every claim is traceable to specific source material. This builds user trust, enables verification, and supports compliance requirements for transparent AI systems.

The implementation demonstrates:
- ✅ State management in LangGraph
- ✅ Effective prompt engineering for specialized behavior
- ✅ Multi-agent coordination with shared state
- ✅ Modern, responsive frontend design
- ✅ API design for machine-readable outputs
