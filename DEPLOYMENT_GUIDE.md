# Feature 4 Deployment Guide

## Overview

This guide walks you through deploying the Feature 4 implementation (Evidence-Aware Answers with Chunk Citations) to a production environment.

## Prerequisites

- Python 3.9+
- Node.js (optional, for frontend build tools)
- Docker (optional, for containerized deployment)
- FastAPI-compatible server (uvicorn, gunicorn, etc.)
- OpenAI API key
- Pinecone API key

## Local Development Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Pinecone Configuration
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=ikms-vectors
PINECONE_ENVIRONMENT=us-west-2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 3. Start the Backend

```bash
# Development server with auto-reload
uvicorn src.app.api:app --reload --host 0.0.0.0 --port 8000

# Or use gunicorn for production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.app.api:app
```

### 4. Test the API

```bash
# Test /qa endpoint with citations
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is HNSW indexing?"
  }' | jq .

# Expected response includes citations dict
```

### 5. Open Frontend

Simply open `index.html` in your browser (use a local web server if CORS issues occur):

```bash
# Python 3
python -m http.server 8080

# Or install and use Live Server in VS Code
# Then navigate to http://localhost:8080
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build Image

```bash
docker build -t ikms-rag:feature4 .
```

### 3. Run Container

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e PINECONE_API_KEY=$PINECONE_API_KEY \
  -e PINECONE_INDEX_NAME=ikms-vectors \
  ikms-rag:feature4
```

### 4. Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - PINECONE_INDEX_NAME=ikms-vectors
      - DEBUG=False
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./index.html:/usr/share/nginx/html/index.html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
    restart: unless-stopped
```

Run with:

```bash
docker-compose up -d
```

## Cloud Deployment Options

### Azure App Service

1. **Create App Service**
   ```bash
   az appservice plan create --name ikms-plan --resource-group myResourceGroup --sku B1 --is-linux
   az webapp create --resource-group myResourceGroup --plan ikms-plan --name ikms-rag --runtime "PYTHON|3.11"
   ```

2. **Deploy Code**
   ```bash
   az webapp up --name ikms-rag --resource-group myResourceGroup
   ```

3. **Configure Environment Variables**
   ```bash
   az webapp config appsettings set --resource-group myResourceGroup --name ikms-rag \
     --settings OPENAI_API_KEY="$OPENAI_API_KEY" PINECONE_API_KEY="$PINECONE_API_KEY"
   ```

### Google Cloud Run

1. **Build and Push Image**
   ```bash
   gcloud builds submit --tag gcr.io/$PROJECT_ID/ikms-rag:feature4
   ```

2. **Deploy**
   ```bash
   gcloud run deploy ikms-rag \
     --image gcr.io/$PROJECT_ID/ikms-rag:feature4 \
     --platform managed \
     --region us-central1 \
     --set-env-vars OPENAI_API_KEY="$OPENAI_API_KEY",PINECONE_API_KEY="$PINECONE_API_KEY"
   ```

### AWS Lambda with API Gateway

Create a `serverless.yml`:

```yaml
service: ikms-rag

provider:
  name: aws
  runtime: python3.11
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
    PINECONE_API_KEY: ${env:PINECONE_API_KEY}

functions:
  api:
    handler: src/app/api.app
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
      - http:
          path: /
          method: ANY
          cors: true
```

Deploy with:
```bash
serverless deploy
```

## Production Checklist

- [ ] **Environment Variables**: All secrets configured (API keys, database URLs)
- [ ] **CORS Configuration**: Frontend and backend CORS settings aligned
- [ ] **Rate Limiting**: Implement rate limiting on `/qa` endpoint
- [ ] **Error Logging**: Configure logging service (e.g., Sentry)
- [ ] **Database**: Pinecone index created and indexed with data
- [ ] **Monitoring**: Set up monitoring (CPU, memory, latency)
- [ ] **Security**: 
  - [ ] HTTPS enabled
  - [ ] API authentication (if needed)
  - [ ] Input validation on backend
- [ ] **Performance**:
  - [ ] Response time < 5 seconds
  - [ ] Connection pooling configured
  - [ ] Caching enabled (if applicable)
- [ ] **Testing**:
  - [ ] Run `test_feature_4.py` in production environment
  - [ ] Test with various question types
  - [ ] Verify citations are generated correctly
- [ ] **Documentation**: README and deployment guide reviewed
- [ ] **Backups**: Database backups scheduled

## Performance Optimization

### 1. Response Caching

Add caching middleware to `src/app/api.py`:

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache2.init(RedisBackend(redis), prefix="ikms-cache")

@app.post("/qa")
@cache(expire=3600)
async def qa_endpoint(payload: QuestionRequest) -> QAResponse:
    # ... existing code
```

### 2. Connection Pooling

Configure Pinecone connection pooling:

```python
from pinecone import init, Index

init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV,
)
# Connection pooling is automatic
```

### 3. Model Batching

For high throughput, batch multiple requests:

```python
@app.post("/qa/batch")
async def batch_qa(requests: list[QuestionRequest]) -> list[QAResponse]:
    # Process multiple requests efficiently
    return [await qa_endpoint(req) for req in requests]
```

## Monitoring & Observability

### Logging Configuration

Add to `src/app/api.py`:

```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@app.post("/qa")
async def qa_endpoint(payload: QuestionRequest) -> QAResponse:
    logger.info(f"Question received: {payload.question[:100]}")
    # ... process question
    logger.info(f"Answer generated with {len(citations)} citations")
```

### Error Tracking

Configure Sentry:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://<key>@<organization>.ingest.sentry.io/<project>",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1
)
```

## Troubleshooting

### Issue: No citations in response

**Cause**: Citation IDs not being generated in retrieval_node

**Solution**:
1. Check that `serialize_chunks_with_citations()` is being called
2. Verify retrieval_tool returns artifact (Document objects)
3. Check agent prompts include citation instructions

### Issue: Missing citations in answer

**Cause**: Agent not following citation instructions

**Solution**:
1. Verify summarization prompt is complete
2. Try with a simpler question first
3. Check OpenAI API response (log raw response)
4. Consider increasing model context window

### Issue: CORS errors in frontend

**Cause**: API not configured for cross-origin requests

**Solution**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Slow responses

**Cause**: Multiple factors (network, model latency, retrieval time)

**Solution**:
1. Enable response caching
2. Optimize retrieval (fewer documents, better queries)
3. Use a faster model if acceptable (gpt-3.5-turbo)
4. Add connection pooling
5. Profile with: `python -m cProfile -s cumtime api.py`

## Rollback Procedure

If issues arise after deployment:

```bash
# Docker: Rollback to previous image
docker ps  # Find container ID
docker stop <container-id>
docker run -p 8000:8000 ikms-rag:feature4-v1.0

# Or with docker-compose
docker-compose down
git checkout <previous-tag>
docker-compose up -d
```

## Maintenance

### Regular Tasks

- **Daily**: Check logs for errors
- **Weekly**: Review performance metrics
- **Monthly**: Update dependencies (`pip list --outdated`)
- **Quarterly**: Security audit, dependency updates

### Backup Strategy

```bash
# Export Pinecone vectors
pinecone.Index(index_name).describe_index_stats()

# Back up configuration files
tar -czf ikms-backup-$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

## Support & Resources

- **Backend Issues**: Check FastAPI logs
- **LLM Issues**: Review OpenAI API status and usage
- **Retrieval Issues**: Check Pinecone dashboard
- **Frontend Issues**: Check browser console (F12)

## Next Steps

After successful deployment:

1. Monitor performance metrics
2. Gather user feedback on citations UI
3. Iterate on prompt engineering
4. Consider implementing additional features (4-5 from the project spec)
5. Plan for scaling
