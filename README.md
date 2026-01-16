# IKMS Multi-Agent RAG - Evidence-Aware Q&A System

## 🚀 Live Deployment

- **Frontend Application**: [https://candid-otter-3f6fa2.netlify.app](https://candid-otter-3f6fa2.netlify.app)
- **Backend API**: [https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com](https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com)
- **API Documentation**: [https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com/docs](https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com/docs)

---

## 📋 Overview

This project is a **Knowledge-Based Question-Answering Application** built with LangChain 1.0, LangGraph, Pinecone vector database, and OpenAI GPT-4o-mini. The system uses a pre-indexed PDF document about vector databases and answers questions using retrieval-augmented generation (RAG) with evidence-aware citations.

### Key Features

- **PDF Document Processing**: Automatically extracts and indexes content from PDF files
- **Vector Search**: Uses Pinecone for efficient semantic search across document content
- **AI-Powered Answers**: Leverages OpenAI GPT-3.5 to generate accurate, context-aware responses
- **Citation Support**: Provides source references for transparency and verification
- **REST API**: FastAPI backend with interactive documentation
- **Modern Frontend**: Clean, responsive user interface

---

## 🏗️ Architecture

### Backend Stack
- **LangChain 1.0**: Orchestration framework for LLM applications
- **LangGraph**: Multi-agent workflow management
- **Pinecone**: Cloud-based vector database for embeddings
- **OpenAI GPT-4o-mini**: Language model for question answering
- **OpenAI text-embedding-3-large**: Embedding model for vectorization
- **FastAPI**: High-performance async web framework
- **PyPDF**: PDF text extraction

### Frontend Stack
- **HTML/CSS/JavaScript**: Lightweight, responsive interface
- **Fetch API**: Communication with backend

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Pinecone API Key
- Git

### Clone the Repository
```bash
git clone https://github.com/biharamalith/IKMS-Multi-Agent-RAG-STEMLINK.git
cd IKMS-Multi-Agent-RAG-STEMLINK
```

### Backend Setup

1. **Create a virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set environment variables**:
```bash
# Create a .env file with:
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=knowledge-index
```

4. **Run the backend**:
```bash
uvicorn src.app.api:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

Simply open `index.html` in a web browser, or serve it using:
```bash
python -m http.server 8080
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `PINECONE_API_KEY` | Your Pinecone API key | Yes |
| `PINECONE_INDEX_NAME` | Name of your Pinecone index | Yes |
| `PINECONE_ENV` | Pinecone environment (e.g., us-central1-gcp) | No |

---

## 🎯 Usage

### Via Web Interface

1. Navigate to the [frontend application](https://candid-otter-3f6fa2.netlify.app)
2. Type a question about vector databases in the text area
3. Click "Ask Question"
4. View AI-generated answers with citations
5. Click on citation links to see source materials

**Sample Questions to Try:**
- What is a vector database?
- How does Pinecone work?
- What are embeddings?
- What is the difference between vector databases and traditional databases?
- How are similarity searches performed in vector databases?
- What are the use cases for vector databases?
- Explain approximate nearest neighbor search
- What is semantic search?

### Via API

**Ask a Question**:
```bash
curl -X POST "https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a vector database?"}'
```

**Response Format**:
```json
{
  "answer": "A vector database is optimized for storing and querying high-dimensional embeddings...",
  "context": "Retrieved context from documents...",
  "citations": {
    "C1": {
      "source": "vector_db_paper.pdf",
      "page": 3,
      "snippet": "Vector databases are optimized for..."
    }
  }
}
```

**Upload a PDF Document**:
```bash
curl -X POST "https://ikms-multi-agent-rag-3cc2c786cc94.herokuapp.com/index-pdf" \
  -F "file=@document.pdf"
```

---

## 📚 API Endpoints

### `GET /`
Health check and API info
- **Output**: Status message with available endpoints

### `POST /qa`
Ask a question about indexed documents
- **Input**: `{"question": "your question"}`
- **Output**: Answer with citations

### `POST /index-pdf`
Upload and index a PDF document
- **Input**: Multipart form data with PDF file
- **Output**: Success message with chunks indexed count

### `GET /docs`
Interactive API documentation (Swagger UI)

---

## 🧪 Development

### Project Structure
```
class-12/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── api.py              # FastAPI application
│       ├── models.py           # Pydantic data models
│       ├── core/
│       │   ├── config.py       # Configuration settings
│       │   ├── agents/         # LangGraph agents
│       │   │   ├── agents.py
│       │   │   ├── graph.py
│       │   │   ├── prompts.py
│       │   │   ├── state.py
│       │   │   └── tools.py
│       │   ├── llm/
│       │   │   └── factory.py  # LLM initialization
│       │   └── retrieval/
│       │       ├── vector_store.py
│       │       └── serialization.py
│       └── services/
│           ├── qa_service.py       # QA orchestration
│           └── indexing_service.py # PDF indexing
├── index.html              # Frontend UI
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuration
├── runtime.txt            # Python version for Heroku
├── Procfile               # Heroku deployment config
└── README.md              # This file
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

---

## 🚢 Deployment

### Backend (Heroku)
```bash
heroku login
heroku create ikms-multi-agent-rag
heroku config:set OPENAI_API_KEY=xxx PINECONE_API_KEY=xxx
git push heroku main
```

### Frontend (Netlify/Vercel)
```bash
# Netlify
netlify deploy --prod

# Vercel
vercel --prod
```

---

## 🛠️ Technologies

- **LangChain 1.0**: LLM application framework
- **LangGraph**: Multi-agent workflow orchestration
- **Pinecone**: Cloud vector database
- **OpenAI GPT-4o-mini**: Large language model
- **OpenAI text-embedding-3-large**: Embedding model
- **FastAPI**: Modern async web framework
- **PyPDF**: PDF processing
- **Uvicorn**: ASGI server
- **Netlify**: Frontend hosting
- **Heroku**: Backend hosting

---

## 📖 Documentation

For detailed implementation guides, see:
- [Building with LangChain](https://python.langchain.com/docs/get_started/introduction)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Bihara Malith** - [GitHub](https://github.com/biharamalith)

---

## 🙏 Acknowledgments

- LangChain team for the excellent framework
- Pinecone for vector database infrastructure
- OpenAI for GPT models
- STEMLINK for project support

---

## 📞 Support

For issues and questions:
- Create an issue in the [GitHub repository](https://github.com/biharamalith/IKMS-Multi-Agent-RAG-STEMLINK/issues)


---

## 🔮 Future Enhancements

- [ ] Support for multiple document formats (DOCX, TXT, etc.)
- [ ] Multi-language support
- [ ] Advanced citation formatting
- [ ] User authentication and document management
- [ ] Conversation history and context retention
- [ ] Integration with more LLM providers
- [ ] Real-time collaboration features

---

**Built with ❤️ for evidence-aware question answering**

