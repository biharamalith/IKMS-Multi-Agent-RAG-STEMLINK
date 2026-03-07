# IKMS Multi-Agent RAG — Full Architecture & Feature 4 Documentation

> **Developed by Bihara Malith**  
> IKMS Multi-Agent RAG System with Evidence-Aware Answers & PDF Upload  
> Live Backend: `https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com`  
> Frontend: Deployed on Netlify from `frontend-deploy/`

---

## What Is This Application?

**IKMS Multi-Agent RAG** is an AI-powered Question & Answer system. A user uploads PDF documents, and then asks questions about them. The system uses **three AI agents working together** (Retrieval → Summarization → Verification) to find the answer from the uploaded documents and **cite exactly which page and paragraph the answer came from** using citation IDs like `[C1]`, `[C2]`, `[C3]`.

### What Makes It Special (Feature 4: Evidence-Aware Answers)

Most AI chatbots give answers but don't tell you **where the answer came from**. Our system:
- Tags every piece of retrieved text with a citation ID (C1, C2, C3...)
- Forces the AI to cite sources like a research paper: `"HNSW provides fast search [C1][C2]."`
- Returns a clickable citation map so the user can verify the source
- A Verification Agent double-checks the answer and removes any unsupported claims

---

## 1. High-Level System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     IKMS Multi-Agent RAG                          │
│            Feature 4: Evidence-Aware Answers + PDF Upload          │
│                     Developed by Bihara Malith                     │
└──────────────────────────────────────────────────────────────────┘

  ┌───────────────────────────┐
  │   Frontend (Netlify)      │  frontend-deploy/index.html
  │   Web Browser             │
  │                           │  Features:
  │   • Ask Questions         │  - Question input + Submit
  │   • Upload PDFs           │  - Drag & drop PDF upload
  │   • View Cited Answers    │  - Answer with clickable [C1][C2]
  │   • Click Citations       │  - Source Materials panel
  └─────────┬─────────────────┘  - Citation highlighting on click
            │
            │  HTTP Requests (fetch API)
            │  ┌──────────────────────────────────────┐
            │  │ POST /qa        → Ask a question     │
            │  │ POST /index-pdf → Upload a PDF       │
            │  │ GET  /health    → Check if alive     │
            │  └──────────────────────────────────────┘
            │
            ▼
  ┌──────────────────────────────────────────────────────────────┐
  │      FastAPI Backend (Heroku)   src/app/api.py               │
  │      https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com │
  ├──────────────────────────────────────────────────────────────┤
  │  CORS Middleware — allows frontend on any domain to connect  │
  │                                                              │
  │  Endpoints:                                                  │
  │  GET  /         → API status info                            │
  │  GET  /health   → {"status": "healthy"}                      │
  │  GET  /docs     → Swagger UI (auto-generated)                │
  │  POST /qa       → Multi-agent Q&A pipeline                   │
  │  POST /index-pdf → PDF upload + Pinecone indexing            │
  └─────────┬────────────────────────────────────────────────────┘
            │
   ┌────────┴──────────────────────────────────┐
   │                                           │
   ▼ (for /qa)                                 ▼ (for /index-pdf)
  ┌──────────────────────┐     ┌─────────────────────────────────┐
  │ qa_service.py        │     │ indexing_service.py              │
  │ → run_qa_flow()      │     │ → index_documents(file_path)    │
  └──────┬───────────────┘     │   PyPDFLoader → split → embed   │
         │                     │   → upsert into Pinecone        │
         ▼                     └──────────┬──────────────────────┘
  ┌──────────────────────────────┐        │
  │ LangGraph State Machine      │        │
  │ graph.py                     │        │
  │                              │        │
  │ START                        │        │
  │   → retrieval_node           │        │
  │     → summarization_node     │        │
  │       → verification_node    │        │
  │ END                          │        │
  └──────┬───────────────────────┘        │
         │                                │
   ┌─────┴──────────────┐                 │
   ▼                    ▼                 ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
  │ Pinecone DB  │  │ OpenAI API   │  │ Pinecone DB          │
  │ (Retrieve)   │  │ (gpt-4o-mini)│  │ (Index/Store)        │
  │              │  │              │  │                      │
  │ ikms-vectors │  │ Embeddings:  │  │ Embeddings:          │
  │ index        │  │ text-embed-  │  │ text-embedding-      │
  │              │  │ ding-3-large │  │ 3-large              │
  └──────────────┘  └──────────────┘  └──────────────────────┘
```

## 2. Project File Structure — What Each File Does

```
class-12/
│
├── .env                          ← API keys (NOT committed to Git)
├── .python-version               ← Python version for Heroku (3.11)
├── Procfile                      ← Heroku start command
├── requirements.txt              ← Python dependencies
│
├── frontend-deploy/
│   └── index.html                ← FRONTEND (deployed to Netlify)
│
├── src/
│   └── app/
│       ├── api.py                ← FastAPI app + all endpoints
│       ├── models.py             ← Request/Response Pydantic models
│       │
│       ├── services/
│       │   ├── qa_service.py     ← Calls the LangGraph pipeline
│       │   └── indexing_service.py ← Calls PDF indexer
│       │
│       └── core/
│           ├── config.py         ← Loads .env settings via Pydantic
│           │
│           ├── llm/
│           │   └── factory.py    ← Creates ChatOpenAI (gpt-4o-mini)
│           │
│           ├── agents/
│           │   ├── state.py      ← QAState TypedDict (question, answer, citations...)
│           │   ├── prompts.py    ← System prompts for all 3 agents
│           │   ├── tools.py      ← retrieval_tool (searches Pinecone)
│           │   ├── agents.py     ← 3 node functions (retrieval, summarization, verification)
│           │   └── graph.py      ← LangGraph StateGraph (wires the 3 nodes)
│           │
│           └── retrieval/
│               ├── vector_store.py    ← Pinecone connection, retrieve(), index_documents()
│               └── serialization.py   ← serialize_chunks_with_citations() — CORE of Feature 4
```

---

## 3. How the Frontend Communicates with the Backend (Code Level)

### Frontend → Backend Connection

The frontend is a **single HTML file** deployed on Netlify. It talks to the Heroku backend using JavaScript `fetch()` API calls.

**Connection Setup** (in `frontend-deploy/index.html`):
```javascript
// This URL points to the Heroku backend
const API_BASE_URL = 'https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com';
```

### User Action 1: Ask a Question

When user types a question and clicks "Ask":

```javascript
// frontend-deploy/index.html — submitQuestion()
async function submitQuestion() {
    const question = document.getElementById('questionInput').value.trim();

    const response = await fetch(`${API_BASE_URL}/qa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),  // sends: {"question": "What is HNSW?"}
    });

    const data = await response.json();
    // data = { answer: "...[C1][C2]", context: "...", citations: {C1: {...}, C2: {...}} }
    displayAnswer(data);
}
```

**Backend receives it** (in `src/app/api.py`):
```python
@app.post("/qa", response_model=QAResponse)
async def qa_endpoint(payload: QuestionRequest) -> QAResponse:
    question = payload.question.strip()       # "What is HNSW?"
    result = answer_question(question)         # runs the 3-agent pipeline
    return QAResponse(
        answer=result.get("answer", ""),       # "HNSW is...[C1][C2]"
        context=result.get("context", ""),     # "[C1] Chunk from page 5:..."
        citations=result.get("citations"),     # {"C1": {"page": 5, ...}, "C2": {...}}
    )
```

### User Action 2: Upload a PDF

When user drags or selects a PDF file:

```javascript
// frontend-deploy/index.html — uploadPDF()
async function uploadPDF() {
    const formData = new FormData();
    formData.append('file', selectedFile);     // the PDF file

    const response = await fetch(`${API_BASE_URL}/index-pdf`, {
        method: 'POST',
        body: formData,                        // multipart file upload
    });

    const data = await response.json();
    // data = { filename: "paper.pdf", chunks_indexed: 24, message: "PDF indexed..." }
}
```

**Backend receives it** (in `src/app/api.py`):
```python
@app.post("/index-pdf")
async def index_pdf(file: UploadFile = File(...)) -> dict:
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    contents = await file.read()
    file_path.write_bytes(contents)            # save PDF to disk

    chunks_indexed = index_pdf_file(file_path)  # split + embed + store in Pinecone

    return {
        "filename": file.filename,
        "chunks_indexed": chunks_indexed,      # e.g., 24
        "message": "PDF indexed successfully.",
    }
```

### CORS — Why the Frontend Can Talk to the Backend

The frontend (Netlify) is on a different domain than the backend (Heroku). Browsers block this by default ("Same-Origin Policy"). We enable it with:

```python
# src/app/api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow any frontend domain
    allow_credentials=True,
    allow_methods=["*"],       # allow POST, GET, etc.
    allow_headers=["*"],       # allow Content-Type, etc.
)
```

---

## 4. The Three AI Agents — How They Work Together

This is the **core of the system**. Three agents run one after another in a **LangGraph pipeline**.

### Pipeline Flow (defined in `src/app/core/agents/graph.py`):

```python
builder = StateGraph(QAState)

builder.add_node("retrieval", retrieval_node)        # Agent 1
builder.add_node("summarization", summarization_node) # Agent 2
builder.add_node("verification", verification_node)   # Agent 3

# Linear flow: START → retrieval → summarization → verification → END
builder.add_edge(START, "retrieval")
builder.add_edge("retrieval", "summarization")
builder.add_edge("summarization", "verification")
builder.add_edge("verification", END)
```

### Shared State (defined in `src/app/core/agents/state.py`):

All three agents read from and write to the **same state dictionary**:

```python
class QAState(TypedDict):
    question: str                       # User's question
    context: str | None                 # Retrieved chunks with [C1], [C2] IDs
    draft_answer: str | None            # Summarization agent's answer
    answer: str | None                  # Final verified answer
    citations: dict[str, dict] | None   # {"C1": {"page": 5, "source": "..."}}
    raw_docs: list | None               # Original Document objects
```

### Agent 1: Retrieval Agent (in `agents.py → retrieval_node()`)

**What it does:** Searches Pinecone for document chunks relevant to the question.

```python
def retrieval_node(state: QAState) -> QAState:
    question = state["question"]

    # Uses create_react_agent from langgraph.prebuilt with retrieval_tool
    agent = _get_retrieval_agent()
    result = agent.invoke({"messages": [HumanMessage(content=question)]})

    # Extract tool results — the ToolMessage contains retrieved documents
    for msg in reversed(result["messages"]):
        if isinstance(msg, ToolMessage):
            context = str(msg.content)
            if hasattr(msg, "artifact") and msg.artifact:
                raw_docs = msg.artifact
                # THIS IS THE KEY — generate citation IDs
                context, citations = serialize_chunks_with_citations(raw_docs)
            break

    return {"context": context, "raw_docs": raw_docs, "citations": citations}
```

**The retrieval_tool** (in `tools.py`):
```python
@tool(response_format="content_and_artifact")
def retrieval_tool(query: str):
    docs = retrieve(query, k=4)    # searches Pinecone for 4 most relevant chunks
    context, citations = serialize_chunks_with_citations(docs)
    return context, docs           # returns both text + raw Document objects
```

### Agent 2: Summarization Agent (in `agents.py → summarization_node()`)

**What it does:** Reads the context (with [C1], [C2] tags) and writes a draft answer.

```python
def summarization_node(state: QAState) -> QAState:
    question = state["question"]
    context = state.get("context")

    user_content = f"Question: {question}\n\nContext:\n{context}"

    llm = create_chat_model()  # gpt-4o-mini
    messages = [
        SystemMessage(content=SUMMARIZATION_SYSTEM_PROMPT),  # "Cite with [C1]..."
        HumanMessage(content=user_content),
    ]
    response = llm.invoke(messages)

    return {"draft_answer": response.content}
```

**The prompt tells it to cite** (in `prompts.py`):
```
"When generating your answer, you MUST cite your sources using chunk IDs.
 Format: 'Statement here [C1].' or 'Complex statement [C1][C2][C3].'
 Only cite chunks that are actually present in the context."
```

### Agent 3: Verification Agent (in `agents.py → verification_node()`)

**What it does:** Checks the draft answer against the original context, removes hallucinations, keeps citations.

```python
def verification_node(state: QAState) -> QAState:
    question = state["question"]
    context = state.get("context", "")
    draft_answer = state.get("draft_answer", "")

    user_content = f"""Question: {question}
Context: {context}
Draft Answer: {draft_answer}
Please verify and correct the draft answer."""

    llm = create_chat_model()  # gpt-4o-mini
    messages = [
        SystemMessage(content=VERIFICATION_SYSTEM_PROMPT),  # "Maintain citations..."
        HumanMessage(content=user_content),
    ]
    response = llm.invoke(messages)

    return {"answer": response.content}
```

---

## 5. Feature 4: Citation Generation — The Core Innovation

### How Citation IDs Are Created (in `serialization.py`):

```python
def serialize_chunks_with_citations(docs):
    context_parts = []
    citation_map = {}

    for idx, doc in enumerate(docs, start=1):
        chunk_id = f"C{idx}"          # C1, C2, C3, C4
        page_num = doc.metadata.get("page", "unknown")
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content.strip()

        citation_map[chunk_id] = {
            "page": page_num,
            "snippet": content[:100] + "...",
            "source": source,
            "full_content": content,
        }

        context_parts.append(f"[{chunk_id}] Chunk from page {page_num}:\n{content}")

    return "\n\n".join(context_parts), citation_map
```

### Example Output:

**Input:** 4 Document objects retrieved from Pinecone

**Output context string:**
```
[C1] Chunk from page 3:
Vector databases are optimized for storing and querying high-dimensional
embeddings generated by machine learning models...

[C2] Chunk from page 8:
Inverted File (IVF) indexing partitions the vector space into Voronoi cells...

[C3] Chunk from page 9:
Product Quantization (PQ) is a compression technique that divides vectors...

[C4] Chunk from page 10:
Approximate Nearest Neighbor (ANN) search is essential for scaling...
```

**Output citation map:**
```json
{
    "C1": {"page": 3, "source": "vector_db_paper.pdf", "snippet": "Vector databases are optimized for..."},
    "C2": {"page": 8, "source": "vector_db_paper.pdf", "snippet": "Inverted File (IVF) indexing..."},
    "C3": {"page": 9, "source": "vector_db_paper.pdf", "snippet": "Product Quantization (PQ) is..."},
    "C4": {"page": 10, "source": "vector_db_paper.pdf", "snippet": "Approximate Nearest Neighbor..."}
}
```

---

## 6. PDF Upload & Indexing Flow (Document Upload Feature)

```
User drops PDF on frontend
    │
    ▼
Frontend JavaScript: uploadPDF()
    │  POST /index-pdf with FormData (multipart file)
    ▼
api.py: index_pdf()
    │  • Validates file is PDF
    │  • Saves to data/uploads/filename.pdf
    │  • Calls index_pdf_file(file_path)
    ▼
indexing_service.py: index_pdf_file()
    │  • Calls index_documents(file_path)
    ▼
vector_store.py: index_documents()
    │  • PyPDFLoader loads PDF → list of Document objects
    │  • RecursiveCharacterTextSplitter splits into 500-char chunks
    │  • OpenAIEmbeddings converts chunks to vectors (text-embedding-3-large)
    │  • PineconeVectorStore upserts vectors into "ikms-vectors" index
    ▼
Returns: number of chunks indexed (e.g., 24)
    │
    ▼
Frontend shows: "Successfully indexed paper.pdf — 24 chunks created"
```

---

## 7. Complete Data Flow: Question → Answer with Citations

```
USER: "What is a vector database?"
    │
    ▼ [Frontend sends POST /qa with JSON body]
    │
    ▼ api.py receives {"question": "What is a vector database?"}
    │
    ▼ qa_service.py → run_qa_flow("What is a vector database?")
    │
    ▼ graph.py creates initial state:
    │  {
    │    "question": "What is a vector database?",
    │    "context": None, "draft_answer": None, "answer": None,
    │    "citations": None, "raw_docs": None
    │  }
    │
    ▼ ═══════════════════════════════════════════════
    │  AGENT 1: RETRIEVAL NODE
    │  ─────────────────────────
    │  • Sends question to create_react_agent
    │  • Agent calls retrieval_tool("What is a vector database?")
    │  • retrieval_tool → vector_store.retrieve(query, k=4)
    │    → Pinecone similarity search → returns 4 Document objects
    │  • serialize_chunks_with_citations(docs) generates:
    │    context = "[C1] Chunk from page 3:\nVector databases are..."
    │    citations = {"C1": {"page": 3, "source": "paper.pdf", ...}}
    │
    │  State after: context="[C1]...[C2]...", citations={C1:..., C2:...}
    │ ═══════════════════════════════════════════════
    │
    ▼ ═══════════════════════════════════════════════
    │  AGENT 2: SUMMARIZATION NODE
    │  ─────────────────────────────
    │  • Reads question + context (with [C1], [C2] tags)
    │  • System prompt says: "MUST cite sources with [C1], [C2]"
    │  • LLM (gpt-4o-mini) generates:
    │    "A vector database is optimized for storing and querying
    │     high-dimensional embeddings [C1]. It features specialized
    │     indexing structures for similarity search [C1]."
    │
    │  State after: draft_answer="A vector database is...[C1]..."
    │ ═══════════════════════════════════════════════
    │
    ▼ ═══════════════════════════════════════════════
    │  AGENT 3: VERIFICATION NODE
    │  ───────────────────────────
    │  • Reads question + context + draft_answer
    │  • System prompt: "Check all claims. Remove unsupported ones.
    │    Maintain all valid citations."
    │  • LLM verifies each claim against context
    │  • Produces final answer with citations preserved
    │
    │  State after: answer="A vector database is...[C1]."
    │ ═══════════════════════════════════════════════
    │
    ▼ api.py creates QAResponse:
    │  {
    │    "answer": "A vector database is optimized for...[C1].",
    │    "context": "[C1] Chunk from page 3:\nVector databases...",
    │    "citations": {
    │      "C1": {"page": 3, "source": "vector_db_paper.pdf",
    │             "snippet": "Vector databases are optimized for..."}
    │    }
    │  }
    │
    ▼ [HTTP 200 OK, JSON response sent to frontend]
    │
    ▼ Frontend displayAnswer(data):
    │  • Parses answer text, converts [C1] to clickable <span> elements
    │  • Renders Source Materials panel with citation metadata
    │  • Shows stats: "1 Citations Found | 4 Chunks Retrieved"
    │
    ▼ USER SEES:
    ┌────────────────────────────────────────────────┐
    │ Answer:                                        │
    │ "A vector database is optimized for storing    │
    │  and querying high-dimensional embeddings [C1].│
    │  It features specialized indexing structures    │
    │  for similarity search [C1]."                  │
    │                                                │
    │ Source Materials:                               │
    │ ┌──────────────────────────────────────────┐   │
    │ │ C1  Source: vector_db_paper.pdf           │   │
    │ │     Page: 3                               │   │
    │ │     "Vector databases are optimized for   │   │
    │ │      storing and querying high-dimens..." │   │
    │ └──────────────────────────────────────────┘   │
    └────────────────────────────────────────────────┘
```

---

## 8. Frontend Citation Interaction — How Clicking Works

```javascript
// When answer is displayed, [C1] becomes a clickable span:
function highlightCitations(answer) {
    return answer.replace(/\[C(\d+)\]/g, (match, num) => {
        return `<span class="citation-link"
                 onclick="highlightCitation('C${num}')">[C${num}]</span>`;
    });
}

// When user clicks [C1]:
function highlightCitation(citationId) {
    // 1. Remove previous highlights
    document.querySelectorAll('.citation-link.active, .citation-item.active')
        .forEach(el => el.classList.remove('active'));

    // 2. Highlight the clicked citation in the answer text
    document.querySelectorAll('.citation-link').forEach(el => {
        if (el.textContent === `[${citationId}]`) el.classList.add('active');
    });

    // 3. Highlight + scroll to the source in the Citations panel
    const citationItem = document.getElementById(`citation-${citationId}`);
    if (citationItem) {
        citationItem.classList.add('active');
        citationItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}
```

**Visual Result:**
```
┌──────────────────────────────────────────┐
│  Answer Text:                            │
│  "A vector database is optimized for     │
│   storing embeddings [C1]."              │
│                        ^^^^              │
│                   (highlighted blue)      │
│                                          │
│  Source Materials:                        │
│  ┌──────────────────────────────────┐    │
│  │ ▌ C1  (highlighted with border) │    │
│  │   Source: vector_db_paper.pdf    │    │
│  │   Page: 3                        │    │
│  │   "Vector databases are..."      │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

---

## 9. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML/CSS/JavaScript | Single-page UI |
| **Frontend Hosting** | Netlify | Static site hosting |
| **Backend Framework** | FastAPI (Python) | REST API server |
| **Backend Hosting** | Heroku | Cloud app platform |
| **AI Orchestration** | LangGraph | Multi-agent pipeline |
| **LLM** | OpenAI gpt-4o-mini | Text generation |
| **Embeddings** | OpenAI text-embedding-3-large | Vector representation |
| **Vector Database** | Pinecone (ikms-vectors) | Similarity search |
| **PDF Processing** | PyPDFLoader | Extract text from PDFs |
| **Text Splitting** | RecursiveCharacterTextSplitter | Split docs to 500-char chunks |
| **Configuration** | Pydantic Settings + .env | Secure config management |

---

## 10. API Response Format — What the User Receives

### POST /qa Response:
```json
{
    "answer": "A vector database is optimized for storing and querying high-dimensional embeddings generated by machine learning models. It features specialized indexing structures and query capabilities designed for similarity search operations [C1].",
    "context": "[C1] Chunk from page 3:\nVector databases are optimized for storing...\n\n[C2] Chunk from page 8:\nInverted File (IVF) indexing...",
    "citations": {
        "C1": {
            "page": 3,
            "snippet": "Vector databases are optimized for storing and querying high-dimensional...",
            "source": "vector_db_paper.pdf",
            "full_content": "Vector databases are optimized for storing and querying high-dimensional embeddings generated by machine learning models. They provide specialized indexing structures and query capabilities designed for similarity search operations."
        },
        "C2": {
            "page": 8,
            "snippet": "Inverted File (IVF) indexing partitions the vector space into Voronoi cells...",
            "source": "vector_db_paper.pdf",
            "full_content": "Inverted File (IVF) indexing partitions the vector space..."
        }
    }
}
```

### POST /index-pdf Response:
```json
{
    "filename": "my_document.pdf",
    "chunks_indexed": 24,
    "message": "PDF indexed successfully."
}
```

### GET /health Response:
```json
{
    "status": "healthy"
}
```

---

## 11. Environment Configuration

All secrets are stored in environment variables (`.env` locally, Heroku Config Vars in production):

```python
# src/app/core/config.py
class Settings(BaseSettings):
    openai_api_key: str                                    # OpenAI API key
    openai_model_name: str = "gpt-4o-mini"                 # LLM model
    openai_embedding_model_name: str = "text-embedding-3-large"  # Embedding model
    pinecone_api_key: str                                  # Pinecone API key
    pinecone_index_name: str                               # "ikms-vectors"
    retrieval_k: int = 4                                   # Number of chunks to retrieve

    model_config = SettingsConfigDict(env_file=".env")     # loads from .env file
```

---

## 12. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                     │
│  github.com/biharamalith/IKMS-Multi-Agent-RAG-STEMLINK  │
│                                                         │
│  git push origin main ──→ triggers Netlify auto-deploy  │
│  git push heroku main ──→ triggers Heroku build+deploy  │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌───────────────────────────┐
│  Netlify          │  HTTP   │  Heroku                    │
│  Frontend         │ ◄─────► │  Backend                   │
│                   │  fetch  │                            │
│  Serves:          │         │  Runs:                     │
│  index.html       │         │  uvicorn src.app.api:app   │
│  (static files)   │         │  --host 0.0.0.0            │
│                   │         │  --port $PORT               │
│  Domain:          │         │                            │
│  *.netlify.app    │         │  Domain:                   │
│                   │         │  ikms-multi-agent-rag-     │
│                   │         │  3cc2c786cc94.herokuapp.com│
└──────────────────┘          └───────────────────────────┘
```
