# SentinelOps

SentinelOps is a real-time incident management system built with FastAPI, providing RESTful APIs and WebSocket support for monitoring and managing incidents.

## Features

- Incident creation, retrieval, and management
- Real-time updates via WebSocket
- RESTful API endpoints
- Database integration with SQLAlchemy
- Pydantic models for data validation
- Asynchronous operations with FastAPI
- **AI-Powered Incident Analysis** - Uses Google Gemini via `google-genai` to analyze logs and metrics for intelligent root cause analysis

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SentinelOps
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   env\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   LLM_PROVIDER=gemini
   GEMINI_MODEL=gemini-3-flash-preview
   ```

## Running the Application

Start the server with auto-reload:
```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## WebSocket

Real-time incident updates are available via WebSocket at `ws://localhost:8000/ws/incidents`

## AI Incident Analysis

SentinelOps includes AI-powered incident analysis that can:

- Analyze system logs and metrics
- Identify potential root causes
- Provide recommended actions
- Assess incident severity
- Generate confidence scores

### Using AI Analysis

1. **Automatic Analysis**: Incidents created by the monitoring simulator automatically trigger AI analysis
2. **Manual Analysis**: Use the `/incidents/analyze` endpoint to analyze specific logs and metrics

Example API call:
```bash
curl -X POST "http://localhost:8000/incidents/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "logs": "[2024-01-15 10:30:45] ERROR redis: Connection timeout",
    "metrics": {
      "cpu_usage": 95,
      "memory_usage": 88,
      "api_error_rate": 0.15,
      "db_latency_ms": 2500
    }
  }'
```

## Project Structure

- `app/main.py`: FastAPI application entry point
- `app/api/`: API route handlers
- `app/core/`: Core functionality (database, etc.)
- `app/models/`: Database models
- `app/schemas/`: Pydantic schemas
- `app/services/`: Business logic services
- `app/websocket/`: WebSocket handlers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.