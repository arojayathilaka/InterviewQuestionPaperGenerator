# Interview Question Paper Generator

A full-stack application that generates customized interview question papers using AI agents and Azure cloud services.

## Overview

This application uses:
- **Backend**: FastAPI with Python
- **Frontend**: React with TypeScript
- **AI**: Claude/OpenAI APIs for intelligent question generation
- **Cloud**: Azure Service Bus, Cosmos DB, and Blob Storage

### Key Features

- **AI-Powered Question Generation**: Uses multiple AI agents to analyze topics and generate questions
- **Async Task Processing**: Leverages Azure Service Bus for scalable background processing
- **Cloud Storage**: Questions and papers stored in Azure Blob Storage
- **Database**: User profiles and metadata in Azure Cosmos DB
- **Retry Logic**: Built-in error handling and automatic retry mechanisms
- **RESTful API**: Clean API for paper generation and retrieval

## Project Structure

```
InterviewQuestionPaperGenerator/
├── backend/
│   ├── app/
│   │   ├── agents/              # AI agents for different tasks
│   │   │   ├── base_agent.py
│   │   │   ├── topic_analyzer.py
│   │   │   ├── question_generator.py
│   │   │   ├── difficulty_calibrator.py
│   │   │   └── paper_formatter.py
│   │   ├── services/            # Azure service integrations
│   │   │   ├── service_bus.py
│   │   │   ├── cosmos_db.py
│   │   │   ├── blob_storage.py
│   │   │   └── orchestration.py
│   │   ├── routes/              # API endpoints
│   │   │   ├── papers.py
│   │   │   └── users.py
│   │   ├── models/              # Pydantic schemas
│   │   ├── config/              # Configuration
│   │   ├── utils/               # Utilities (errors, logging, helpers)
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py                   # Entry point
│
└── frontend/
    ├── src/
    │   ├── components/          # React components
    │   │   ├── PaperGenerationForm.jsx
    │   │   ├── PaperResults.jsx
    │   │   └── UserRegistration.jsx
    │   ├── pages/               # Pages
    │   │   └── HomePage.jsx
    │   ├── services/            # API client
    │   │   └── api.js
    │   ├── App.jsx
    │   ├── index.jsx
    │   └── index.css
    ├── package.json
    ├── tailwind.config.js
    └── .env.example
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- Azure Subscription (for cloud services)
- OpenAI or Anthropic API key

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `AZURE_SERVICE_BUS_CONNECTION_STRING`
- `COSMOS_DB_CONNECTION_STRING`
- `AZURE_STORAGE_ACCOUNT_NAME`
- `AZURE_STORAGE_ACCOUNT_KEY`
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

### 3. Run the Backend

```bash
python run.py
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

### 3. Start Development Server

```bash
npm start
```

The application will be available at `http://localhost:3000`

## API Endpoints

### Paper Generation

#### Generate a Question Paper
```
POST /api/v1/papers/generate
```

Request body:
```json
{
  "user_id": "user123",
  "technology_topic": "Python Async Programming",
  "num_questions": 10,
  "difficulty_level": "mixed",
  "question_types": ["multiple_choice"],
  "duration_minutes": 60,
  "preferences": "Focus on best practices"
}
```

Response:
```json
{
  "status": "queued",
  "paper_id": "paper_abc123xyz",
  "message": "Paper generation has been queued..."
}
```

#### Get Paper Status
```
GET /api/v1/papers/status/{paper_id}
```

#### Get Generated Paper
```
GET /api/v1/papers/{paper_id}
```

### User Management

#### Register User
```
POST /api/v1/users/register
```

Request body:
```json
{
  "user_id": "user123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

#### Get User Profile
```
GET /api/v1/users/{user_id}
```

## AI Agents

The system uses four specialized AI agents:

### 1. TopicAnalyzerAgent
- Analyzes the technology topic
- Breaks it into subtopics
- Identifies key concepts
- Suggests difficulty distribution

### 2. QuestionGeneratorAgent
- Generates questions based on topic analysis
- Supports multiple question types
- Maintains specified difficulty levels
- Includes explanations for answers

### 3. DifficultyCalibratorAgent
- Reviews generated questions
- Calibrates difficulty levels
- Ensures distribution matches targets
- Optimizes question balance

### 4. PaperFormatterAgent
- Formats questions into a professional paper
- Generates exam instructions
- Creates answer keys with explanations
- Produces downloadable documents

## Error Handling & Retry Logic

The application includes comprehensive error handling:

- **Validation Errors**: Input validation with clear error messages
- **Retry Configuration**: Exponential backoff for transient failures
- **Logging**: Structured JSON logging for all operations
- **Custom Exceptions**: Specific exceptions for different error types

Retry configuration default:
- Max retries: 3
- Initial delay: 1 second
- Exponential backoff with 2x multiplier
- Max delay: 10 seconds

## Azure Services Integration

### Azure Service Bus
- Asynchronous task queuing
- Scalable message processing
- Dead-letter queue handling

### Azure Cosmos DB
- User profile storage
- Paper metadata persistence
- Flexible document schema

### Azure Blob Storage
- Generated paper storage
- Question paper archival
- SAS URL generation for secure access

## Deployment

### Backend Deployment

#### Docker
```bash
cd backend
docker build -t interview-generator-api .
docker run -p 8000:8000 --env-file .env interview-generator-api
```

#### Azure Container Instances
```bash
az container create \
  --resource-group myResourceGroup \
  --name interview-generator-api \
  --image interview-generator-api:latest \
  --ports 8000 \
  --environment-variables DEBUG=False
```

### Frontend Deployment

#### Build Production Bundle
```bash
cd frontend
npm run build
```

#### Deploy to Azure Static Web Apps
```bash
az staticwebapp create \
  --name interview-generator-ui \
  --source ./frontend \
  --location westus2 \
  --app-location "build" \
  --output-location "build"
```

## Development

### Running Tests (Backend)
```bash
cd backend
pytest
```

### Running Tests (Frontend)
```bash
cd frontend
npm test
```

### Code Style

Backend uses:
- Black for code formatting
- Flake8 for linting
- MyPy for type checking

Frontend uses:
- ESLint for linting
- Prettier for formatting

## Troubleshooting

### Service Bus Connection Issues
- Verify `AZURE_SERVICE_BUS_CONNECTION_STRING` in `.env`
- Check Azure Service Bus queue exists
- Ensure queue name matches `SERVICE_BUS_QUEUE_NAME`

### Cosmos DB Connection Issues
- Verify `COSMOS_DB_CONNECTION_STRING` in `.env`
- Check database and container names
- Ensure proper Azure RBAC permissions

### Blob Storage Issues
- Verify storage account credentials
- Check blob container exists
- Ensure container name matches `BLOB_CONTAINER_NAME`

### AI API Issues
- Verify API key configuration
- Check API provider selection
- Ensure sufficient API quota

## Performance Optimization

- **Async Operations**: All I/O operations are asynchronous
- **Connection Pooling**: Azure service clients maintain connection pools
- **Caching**: Consider implementing caching for frequently accessed data
- **Batch Processing**: Service Bus supports batch processing

## Security Considerations

- Never commit `.env` files to version control
- Use Azure Key Vault for production secrets
- Enable CORS only for trusted origins in production
- Use HTTPS for all API calls in production
- Implement authentication (JWT) for API endpoints
- Validate and sanitize all user inputs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Contact: support@example.com

---

**Created**: February 2026
**Version**: 1.0.0
