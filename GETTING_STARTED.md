# Getting Started Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- Node.js 16+
- Azure Subscription (or use Azurite emulator)
- API Key (OpenAI or Anthropic)

### Backend Setup (5 minutes)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - AZURE_SERVICE_BUS_CONNECTION_STRING
# - COSMOS_DB_CONNECTION_STRING
# - AZURE_STORAGE_ACCOUNT_NAME & ACCOUNT_KEY
# - ANTHROPIC_API_KEY or OPENAI_API_KEY

# Run the backend
python run.py
```

Backend will be available at: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Frontend Setup (5 minutes)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Edit if needed (defaults work for local backend)

# Start development server
npm start
```

Frontend will be available at: `http://localhost:3000`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│                   (localhost:3000)                       │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP REST API
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│               (localhost:8000)                           │
├──────────────────────────────────────────────────────────┤
│  Orchestration Service                                   │
│  ├─ TopicAnalyzerAgent                                  │
│  ├─ QuestionGeneratorAgent                              │
│  ├─ DifficultyCalibratorAgent                           │
│  └─ PaperFormatterAgent                                 │
└────┬─────────────────────────────┬──────────────────────┘
     │                             │
     ▼                             ▼
┌──────────────────┐      ┌──────────────────┐
│ Azure Service    │      │ Claude/OpenAI    │
│ Bus (Queuing)    │      │ APIs             │
└──────────────────┘      └──────────────────┘
     │
     ├─────────────────────┬──────────────────┐
     ▼                     ▼                  ▼
┌──────────────────┬──────────────────┬──────────────────┐
│ Cosmos DB        │ Blob Storage     │ (Optional)       │
│ (Metadata)       │ (Papers)         │ Database Cache   │
└──────────────────┴──────────────────┴──────────────────┘
```

## API Flow Example

### 1. User Registration
```
POST /api/v1/users/register
{
  "user_id": "user123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

### 2. Generate Paper
```
POST /api/v1/papers/generate
{
  "user_id": "user123",
  "technology_topic": "Python Async Programming",
  "num_questions": 10,
  "difficulty_level": "mixed",
  "question_types": ["multiple_choice"],
  "duration_minutes": 60
}

Response:
{
  "status": "queued",
  "paper_id": "paper_abc123xyz"
}
```

### 3. Poll for Status
```
GET /api/v1/papers/status/paper_abc123xyz
```

### 4. Retrieve Paper
```
GET /api/v1/papers/paper_abc123xyz

Response:
{
  "paper_id": "paper_abc123xyz",
  "topic": "Python Async Programming",
  "status": "completed",
  "questions_count": 10,
  "difficulty_distribution": {
    "easy": 3,
    "medium": 5,
    "hard": 2
  },
  "paper_url": "https://..."
}
```

## Development Workflow

### Making Changes

1. **Backend Changes**
   - Edit files in `backend/app/`
   - Backend auto-reloads on file changes (if running with `--reload`)
   - Check logs: `http://localhost:8000/docs` to test

2. **Frontend Changes**
   - Edit files in `frontend/src/`
   - React dev server auto-reloads
   - Check browser console for errors

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Debugging

**Backend**:
- Add breakpoints in VSCode
- Check logs in console
- Use FastAPI interactive docs: `http://localhost:8000/docs`

**Frontend**:
- Use React DevTools browser extension
- Check browser console (F12)
- Use VSCode Debugger

## Configuration

### Environment Variables

**Backend (.env)**:
```
DEBUG=True
AZURE_SERVICE_BUS_CONNECTION_STRING=your_connection
COSMOS_DB_CONNECTION_STRING=your_connection
AZURE_STORAGE_ACCOUNT_NAME=your_name
AZURE_STORAGE_ACCOUNT_KEY=your_key
ANTHROPIC_API_KEY=your_key
AI_PROVIDER=anthropic
AI_MODEL=claude-3-sonnet-20240229
MAX_RETRIES=3
```

**Frontend (.env.local)**:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development
```

## Using Azurite (Local Azure Emulator)

If you don't have Azure services, use Azurite:

```bash
# Install Azurite
npm install -g azurite

# Run in a separate terminal
azurite-blob --blobPort 10000 --queuePort 10001 --tablePort 10002

# Update .env to use local emulator
AZURE_STORAGE_ACCOUNT_NAME=devstoreaccount1
AZURE_STORAGE_ACCOUNT_KEY=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;
```

## Troubleshooting

### Backend Issues

**"Module not found" error**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"Connection refused" to Azure services**
- Check credentials in .env
- Verify Service Bus queue exists
- Check Cosmos DB connection string format
- Use Azurite for local development

**"CORS error" in frontend**
- Backend CORS is configured for all origins by default
- In production, update CORS in `app/main.py`

### Frontend Issues

**"API not found" errors**
- Check `REACT_APP_API_URL` in `.env.local`
- Ensure backend is running
- Check browser console for exact URL

**Port already in use**
```bash
# Change port
PORT=3001 npm start  # or use different port
python -m uvicorn app.main:app --port 8001
```

## Docker Deployment

### Build and Run with Docker Compose

```bash
# Create .env file at root with Azure credentials
cp backend/.env.example .env

# Build and run
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Azurite: Runs in container
```

### Build Individual Images

```bash
# Backend
docker build -f Dockerfile.backend -t interview-generator-api .
docker run -p 8000:8000 --env-file .env interview-generator-api

# Frontend
docker build -f Dockerfile.frontend -t interview-generator-ui .
docker run -p 3000:3000 interview-generator-ui
```

## Production Deployment

### Pre-deployment Checklist

- [ ] All environment variables configured
- [ ] CORS configured for production domain
- [ ] Authentication/Authorization implemented
- [ ] Rate limiting configured
- [ ] Logging and monitoring set up
- [ ] Database backups configured
- [ ] Error alerting configured

### Azure Deployment

1. **Build and Push Images**
```bash
docker build -f Dockerfile.backend -t myregistry.azurecr.io/interview-generator-api:latest .
docker push myregistry.azurecr.io/interview-generator-api:latest
```

2. **Deploy to App Service**
```bash
az container create \
  --resource-group myResourceGroup \
  --name interview-generator-api \
  --image myregistry.azurecr.io/interview-generator-api:latest \
  --ports 8000 \
  --environment-variables-from-file .env
```

## Performance Tuning

- Enable caching for frequently accessed data
- Implement rate limiting
- Use async operations throughout
- Monitor Azure service quotas
- Optimize AI API calls (batch processing)

## Support & Documentation

- API Docs: `http://localhost:8000/docs`
- Backend README: `./backend/README.md`
- Frontend README: `./frontend/README.md`
- Main README: `./README.md`

---

**Happy coding!** 🚀
