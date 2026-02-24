# Backend API Documentation

## Overview

FastAPI backend for Interview Question Paper Generator with Azure integration.

## Features

- ✅ OpenAI & Anthropic Claude API integration
- ✅ Azure Service Bus for async task processing
- ✅ Azure Cosmos DB for user data
- ✅ Azure Blob Storage for paper storage
- ✅ Automatic retry logic with exponential backoff
- ✅ Comprehensive error handling
- ✅ Structured logging

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
DEBUG=True
AZURE_SERVICE_BUS_CONNECTION_STRING=your_connection_string
COSMOS_DB_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_ACCOUNT_NAME=your_account_name
AZURE_STORAGE_ACCOUNT_KEY=your_account_key
ANTHROPIC_API_KEY=your_api_key
AI_PROVIDER=anthropic
AI_MODEL=claude-3-sonnet-20240229
```

## Running

```bash
python run.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload
```

## API Endpoints

See [API Documentation](./BACKEND_API.md) for detailed endpoint descriptions.

## Project Structure

- `app/agents/` - AI agent implementations
- `app/services/` - Azure service integrations
- `app/routes/` - API route handlers
- `app/models/` - Pydantic data models
- `app/config/` - Configuration management
- `app/utils/` - Utilities and helpers

## Architecture

The paper generation workflow:

1. **Topic Analysis** → TopicAnalyzerAgent analyzes the topic
2. **Question Generation** → QuestionGeneratorAgent creates questions
3. **Difficulty Calibration** → DifficultyCalibratorAgent balances difficulty
4. **Paper Formatting** → PaperFormatterAgent formats the final paper
5. **Storage** → Blob Storage saves paper, Cosmos DB saves metadata

All steps are coordinated by `PaperOrchestrationService` through `AsyncServiceBus` for scalability.

## Error Handling

Custom exception hierarchy:
- `ApplicationError` - Base exception
- `ValidationError` - Input validation
- `AzureServiceError` - Azure service issues
- `AIAgentError` - AI agent failures
- `PaperGenerationError` - Workflow errors

## Logging

Structured JSON logging for all operations:

```json
{
  "timestamp": "2024-02-16T10:30:45.123456",
  "level": "INFO",
  "logger": "app.services.orchestration",
  "message": "Starting paper generation",
  "module": "orchestration",
  "function": "generate_paper"
}
```

## Dependencies

See `requirements.txt` for all dependencies.

Key packages:
- fastapi - Web framework
- uvicorn - ASGI server
- azure-servicebus - Service Bus client
- azure-cosmos - Cosmos DB client
- azure-storage-blob - Blob Storage client
- anthropic/openai - AI APIs
- pydantic - Data validation
- tenacity - Retry logic

## Performance

- Async/await for all I/O operations
- Connection pooling for Azure services
- Exponential backoff retry strategy
- Structured batch processing
