# SentinelOps

SentinelOps is a real-time incident management system built with FastAPI, providing RESTful APIs and WebSocket support for monitoring and managing incidents.

## Features

- Incident creation, retrieval, and management
- Real-time updates via WebSocket
- RESTful API endpoints
- Database integration with SQLAlchemy
- Pydantic models for data validation
- Asynchronous operations with FastAPI

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