# Feature 4: Architecture & Data Flow Diagrams

## 1. High-Level System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     IKMS Multi-Agent RAG                      │
│                    Feature 4: Citations                        │
└──────────────────────────────────────────────────────────────┘

┌─────────────────┐
│    Frontend     │  (index.html)
│   Web Browser   │  - Question input form
│                 │  - Answer display with interactive citations
└────────┬────────┘  - Source materials panel
         │           - Citation highlighting
         │ HTTP POST /qa
         │ JSON: {"question": "..."}
         ▼
┌─────────────────────────────────────────────────────────────┐
│         FastAPI Backend (src/app/api.py)                     │
├─────────────────────────────────────────────────────────────┤
│  /qa Endpoint                                                │
│  ├─ Validate question                                        │
│  ├─ Call answer_question() service                          │
│  └─ Return QAResponse with answer + citations + context    │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│       QA Service Layer (src/app/services/qa_service.py)     │
│       (Wraps LangGraph flow)                                │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│           LangGraph State Machine                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  Retrieval   │ → │ Summarization │ → │ Verification │ │
│  │    Agent     │    │    Agent      │    │    Agent     │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                              │
│  State Flow:                                               │
│  • question: str                                           │
│  • context: str (WITH citation IDs [C1], [C2]...)        │
│  • draft_answer: str (with citations)                     │
│  • answer: str (final, with citations)                    │
│  • citations: dict (C1→metadata, C2→metadata...)          │
│  • raw_docs: list (original Document objects)             │
│                                                              │
└────────┬────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         ▼                                         ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│    Pinecone Vector DB    │        │   OpenAI LLM             │
│  (Vector Storage)        │        │  (GPT-3.5-turbo/4)       │
│                          │        │                          │
│ • Document chunks        │        │ • Retrieval Agent        │
│ • Embeddings             │        │ • Summarization Agent    │
│ • Metadata               │        │ • Verification Agent     │
└──────────────────────────┘        └──────────────────────────┘
```

## 2. Data Flow: Question to Answer with Citations

```
User Question
    │
    ▼
"What is HNSW indexing?"
    │
    ▼ [/qa endpoint receives question]
    │
    ▼ [run_qa_flow(question) starts]
    │
    ├─────────────────────────────────────────┐
    │                                         │
    ▼ STEP 1: RETRIEVAL NODE                  │
    │                                         │
    │ • Get question: "What is HNSW...?"     │
    │ • Query Pinecone: retrieve_tool()      │
    │ • Get raw documents: [Doc1, Doc2, ...] │
    │ • NEW: Call serialize_chunks_with...() │
    │ • Generate citation IDs: C1, C2, C3    │
    │                                         │
    │ OUTPUT:                                 │
    │ • context: "[C1] HNSW is...            │
    │            [C2] Indexing method...     │
    │            [C3] Hierarchical graph..." │
    │                                         │
    │ • citations: {                          │
    │     "C1": {"page": 5, "snippet": ...}  │
    │     "C2": {"page": 6, "snippet": ...}  │
    │     "C3": {"page": 7, "snippet": ...}  │
    │   }                                     │
    │                                         │
    │ • raw_docs: [Document, Document, ...]  │
    │                                         │
    └────────────────┬────────────────────────┘
                     │
                     ▼ [State updated]
    ┌────────────────────────────────────────┐
    │                                        │
    ▼ STEP 2: SUMMARIZATION NODE             │
    │                                        │
    │ • Get question + context (WITH [C1].. │
    │ • LLM Agent reads prompts              │
    │ • Prompt: "Cite sources with [C1],..." │
    │ • Generate answer from context         │
    │ • MUST cite: [C1], [C2], [C3]         │
    │                                        │
    │ OUTPUT: draft_answer                   │
    │ "HNSW (Hierarchical Navigable Small    │
    │  World) is a graph-based indexing [C1] │
    │  method that enables fast search [C2]. │
    │  It uses hierarchical structure [C3]"  │
    │                                        │
    └────────────────┬────────────────────────┘
                     │
                     ▼ [State updated]
    ┌────────────────────────────────────────┐
    │                                        │
    ▼ STEP 3: VERIFICATION NODE              │
    │                                        │
    │ • Get question, context, draft_answer │
    │ • Check: All claims supported?        │
    │ • Check: Citations valid?              │
    │ • Remove: Unsupported claims           │
    │ • Maintain: Valid citations            │
    │ • Verify: Citation IDs exist           │
    │                                        │
    │ OUTPUT: answer (final)                 │
    │ "HNSW is a graph-based indexing method │
    │  that enables fast search [C1][C2].    │
    │  It uses a hierarchical structure [C3]"│
    │                                        │
    └────────────────┬────────────────────────┘
                     │
                     ▼ [State returned]
    
Final State:
    {
        "question": "What is HNSW indexing?",
        "context": "[C1] HNSW is...
                    [C2] Indexing method...
                    [C3] Hierarchical graph...",
        "draft_answer": "HNSW....[C1]...[C2]...[C3]",
        "answer": "HNSW....[C1][C2]...[C3]",
        "citations": {
            "C1": {"page": 5, "source": "paper.pdf", "snippet": "..."},
            "C2": {"page": 6, "source": "paper.pdf", "snippet": "..."},
            "C3": {"page": 7, "source": "paper.pdf", "snippet": "..."}
        },
        "raw_docs": [Document, Document, Document]
    }
        │
        ▼ [QAResponse created]
    
API Response:
    {
        "answer": "HNSW....[C1][C2]...[C3]",
        "context": "[C1] HNSW is...[C2]...[C3]...",
        "citations": {
            "C1": {"page": 5, "source": "paper.pdf", "snippet": "..."},
            "C2": {"page": 6, "source": "paper.pdf", "snippet": "..."},
            "C3": {"page": 7, "source": "paper.pdf", "snippet": "..."}
        }
    }
        │
        ▼ [HTTP 200 OK + JSON]
    
Frontend receives and displays:
    
    ┌────────────────────────────────────────┐
    │            Answer Panel                 │
    │                                        │
    │ HNSW (Hierarchical Navigable Small     │
    │ World) is a graph-based indexing       │
    │ method that enables fast search [C1]   │
    │ [C2]. It uses a hierarchical structure │
    │ [C3].                                   │
    │                                        │
    │ [User clicks [C1]]                     │
    └────────────────────────────────────────┘
                    │
                    ▼
    ┌────────────────────────────────────────┐
    │         Source Materials Panel          │
    │         (C1 highlighted)                │
    │                                        │
    │ ▌ C1  (highlighted)                    │
    │   Source: paper.pdf                    │
    │   Page: 5                               │
    │   "HNSW (Hierarchical Navigable Small  │
    │    World) graphs provide logarithmic   │
    │    search complexity..."                │
    │                                        │
    │ ○ C2                                   │
    │   Source: paper.pdf                    │
    │   Page: 6                               │
    │   "The hierarchical structure allows..." │
    │                                        │
    │ ○ C3                                   │
    │   Source: paper.pdf                    │
    │   Page: 7                               │
    │   "Each node maintains connections..." │
    │                                        │
    └────────────────────────────────────────┘
```

## 3. State Schema Evolution

```
START
  │
  ▼
Initial State:
{
    "question": "What is HNSW indexing?",
    "context": None,
    "draft_answer": None,
    "answer": None,
    "citations": None,              ← NEW
    "raw_docs": None                ← NEW
}

  │ [retrieval_node executes]
  ▼

After Retrieval:
{
    "question": "What is HNSW indexing?",
    "context": "[C1] Chunk...\n[C2] Chunk...",  ← UPDATED (with citation IDs)
    "draft_answer": None,
    "answer": None,
    "citations": {                  ← UPDATED (NEW)
        "C1": {"page": 5, "source": "...", ...},
        "C2": {"page": 6, "source": "...", ...},
        "C3": {"page": 7, "source": "...", ...}
    },
    "raw_docs": [Document, ...]     ← UPDATED (NEW)
}

  │ [summarization_node executes]
  ▼

After Summarization:
{
    "question": "What is HNSW indexing?",
    "context": "[C1] Chunk...\n[C2] Chunk...",
    "draft_answer": "HNSW is...[C1]...[C2]...[C3]",  ← UPDATED
    "answer": None,
    "citations": { "C1": {...}, "C2": {...}, "C3": {...} },
    "raw_docs": [Document, ...]
}

  │ [verification_node executes]
  ▼

After Verification (FINAL):
{
    "question": "What is HNSW indexing?",
    "context": "[C1] Chunk...\n[C2] Chunk...",
    "draft_answer": "HNSW is...[C1]...[C2]...[C3]",
    "answer": "HNSW is...[C1][C2]...[C3]",  ← UPDATED (FINAL)
    "citations": { "C1": {...}, "C2": {...}, "C3": {...} },
    "raw_docs": [Document, ...]
}

  │
  ▼
Response to Client:
{
    "answer": "HNSW is...[C1][C2]...[C3]",
    "context": "[C1] Chunk...\n[C2] Chunk...",
    "citations": { "C1": {...}, "C2": {...}, "C3": {...} }
}
```

## 4. Citation ID Generation Process

```
retrieve() from Pinecone
    │
    ▼
Raw Documents
[
    Document {
        page_content: "HNSW is a hierarchical...",
        metadata: {"page": 5, "source": "paper.pdf"}
    },
    Document {
        page_content: "Indexing method provides...",
        metadata: {"page": 6, "source": "paper.pdf"}
    },
    Document {
        page_content: "Hierarchical structure...",
        metadata: {"page": 7, "source": "paper.pdf"}
    }
]
    │
    ▼
serialize_chunks_with_citations()
    │
    ├─→ Loop through docs (idx=1, 2, 3)
    │
    ├─→ For doc[0]:
    │   • chunk_id = "C" + "1" = "C1"
    │   • page = 5
    │   • source = "paper.pdf"
    │   • snippet = first 100 chars
    │   • Context line: "[C1] Chunk from page 5: HNSW is..."
    │   • Citation entry: C1 → {page: 5, source: "paper.pdf", ...}
    │
    ├─→ For doc[1]:
    │   • chunk_id = "C2"
    │   • page = 6
    │   • Context line: "[C2] Chunk from page 6: Indexing method..."
    │   • Citation entry: C2 → {page: 6, source: "paper.pdf", ...}
    │
    └─→ For doc[2]:
        • chunk_id = "C3"
        • page = 7
        • Context line: "[C3] Chunk from page 7: Hierarchical..."
        • Citation entry: C3 → {page: 7, source: "paper.pdf", ...}
    
    ▼
Return:
    (
        context_str: "[C1] Chunk from page 5: HNSW is...\n\n[C2] Chunk from page 6: Indexing method...\n\n[C3] Chunk from page 7: Hierarchical...",
        
        citations: {
            "C1": {
                "page": 5,
                "source": "paper.pdf",
                "snippet": "HNSW is a hierarchical...",
                "full_content": "HNSW is a hierarchical..."
            },
            "C2": {
                "page": 6,
                "source": "paper.pdf",
                "snippet": "Indexing method provides...",
                "full_content": "Indexing method provides..."
            },
            "C3": {
                "page": 7,
                "source": "paper.pdf",
                "snippet": "Hierarchical structure...",
                "full_content": "Hierarchical structure..."
            }
        }
    )
```

## 5. Frontend Citation Interaction Flow

```
┌────────────────────────────────────────┐
│      User Sees Answer in Browser       │
│                                        │
│  "HNSW is a graph-based indexing      │
│   method that enables fast search [C1] │
│   [C2]. It uses hierarchical structure │
│   [C3]."                               │
│                                        │
│  Source Materials:                     │
│  ○ C1 - paper.pdf (Page 5)            │
│  ○ C2 - paper.pdf (Page 6)            │
│  ○ C3 - paper.pdf (Page 7)            │
└────────────────────────────────────────┘
                    │
                    │ User clicks [C1]
                    │
                    ▼
┌────────────────────────────────────────┐
│   JavaScript onclick handler fires     │
│                                        │
│   highlightCitation('C1')              │
│       └─ Add .active class to [C1]    │
│       └─ Add .active class to C1 item │
│       └─ Scroll C1 into view           │
└────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│   Visual Feedback Updates              │
│                                        │
│   Answer Text:                         │
│   "HNSW is a graph-based indexing     │
│    method that enables fast search [C1]│  ← Highlighted in blue
│    [C2]. It uses hierarchical structure│
│    [C3]."                              │
│                                        │
│   Source Materials:                    │
│   ▌ C1 (background color changed)     │  ← Active/highlighted
│   │ Source: paper.pdf                 │
│   │ Page: 5                            │
│   │ "HNSW is a hierarchical Navigable"│
│   │                                    │
│   ○ C2                                │
│   ○ C3                                │
└────────────────────────────────────────┘
```

## 6. Component Interaction Diagram

```
                    ┌─────────────────────────────────┐
                    │        index.html               │
                    │    (Frontend UI)                │
                    └───────────────┬─────────────────┘
                                    │
                    ┌───────────────┴─────────────────┐
                    │ Fetch /qa endpoint              │
                    ▼
        ┌───────────────────────────────────────────┐
        │         api.py (/qa endpoint)            │
        │                                           │
        │ • Validate question                      │
        │ • Call answer_question(question)         │
        │ • Extract citations from result          │
        │ • Return QAResponse                      │
        └──────────────┬────────────────────────────┘
                       │
                       ▼
        ┌───────────────────────────────────────────┐
        │      qa_service.py                       │
        │                                           │
        │ • Call run_qa_flow(question)             │
        │ • Return result dict                     │
        └──────────────┬────────────────────────────┘
                       │
                       ▼
        ┌───────────────────────────────────────────┐
        │         graph.py                         │
        │                                           │
        │  START → retrieval → summarization →     │
        │          verification → END              │
        └──────────────┬────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    ┌─────────┐  ┌──────────┐  ┌────────────┐
    │retrieval│  │summarize │  │ verify     │
    │_node    │  │_node     │  │_node       │
    └────┬────┘  └────┬─────┘  └────┬───────┘
         │            │             │
         ▼            │             │
    ┌──────────────┐  │             │
    │ tools.py     │  │             │
    │retrieval_tool│  │             │
    └────┬─────────┘  │             │
         │            │             │
    ┌────┴────────────┼─────────────┴──────┐
    ▼                 ▼                    ▼
┌──────────┐    ┌──────────────┐  ┌──────────────┐
│Pinecone  │    │ prompts.py   │  │prompts.py    │
│Vector DB │    │SUMMARIZATION │  │VERIFICATION  │
└──────────┘    │_PROMPT       │  │_PROMPT       │
                └──────────────┘  └──────────────┘
                       ▼                  ▼
                ┌──────────────────────────────────┐
                │      OpenAI API                  │
                │   (GPT-3.5-turbo / GPT-4)       │
                │                                  │
                │  • Summarization Agent          │
                │  • Verification Agent           │
                └──────────────────────────────────┘
                       ▲
                       │
                ┌──────┴──────────────────────────┐
                │                                  │
         ┌──────┴──────────┐      ┌───────────────┴─────┐
         ▼                 ▼      ▼                     ▼
    ┌─────────┐   ┌──────────────────┐    ┌─────────────────┐
    │question │   │context WITH [C1] │    │draft_answer WITH │
    │         │   │[C2][C3]...       │    │[C1][C2][C3]...  │
    └─────────┘   └──────────────────┘    └─────────────────┘
```

## 7. Citation Preservation Through Verification

```
Input (from Summarization):
    answer = "HNSW provides fast search [C1][C2]. It uses hierarchical structure [C3]. 
              LSH is slower [C4]."
    
    context = "[C1] HNSW...[C2] Provides...[C3] Hierarchical...[C4] LSH..."

Verification checks:
    [C1] CLAIM: "HNSW provides fast search" → ✓ Valid (in context)
    [C2] CLAIM: "HNSW provides fast search" → ✓ Valid (in context)
    [C3] CLAIM: "uses hierarchical structure" → ✓ Valid (in context)
    [C4] CLAIM: "LSH is slower" → ✗ Not in context (REMOVE)

Output (Verification):
    answer = "HNSW provides fast search [C1][C2]. It uses hierarchical structure [C3]."
    
    Removed: "[C4]" (claim removed, citation removed)
    Kept: "[C1]", "[C2]", "[C3]" (claims verified, citations preserved)
```

---

These diagrams illustrate how Feature 4 integrates citation tracking throughout the entire system, from retrieval through verification to the final API response and frontend display.
