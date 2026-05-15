# OrkestrAI Backend

FastAPI-based backend for OrkestrAI multi-agent orchestration platform.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- IBM watsonx API credentials

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Run database migrations:
```bash
# Database will be auto-created on first run
```

5. Start development server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── agents/               # AI agent implementations
│   ├── core/                 # Core utilities
│   ├── db/                   # Database models and session
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   ├── config.py             # Configuration
│   └── main.py               # FastAPI app entry point
├── requirements.txt          # Python dependencies
└── .env.example             # Environment template
```

## Key Endpoints

### Projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `GET /api/v1/projects` - List all projects
- `DELETE /api/v1/projects/{id}` - Delete project

### Orchestration
- `GET /api/v1/orchestration/{id}/status` - Get orchestration status
- `POST /api/v1/orchestration/{id}/start` - Start orchestration

### WebSocket
- `WS /api/v1/ws/orchestration/{id}` - Real-time updates

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black app/

# Lint
flake8 app/
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `WATSONX_API_KEY` - IBM watsonx API key
- `WATSONX_PROJECT_ID` - IBM watsonx project ID
- `SECRET_KEY` - Secret key for JWT tokens

Optional:
- `GITHUB_CLIENT_ID` - GitHub OAuth client ID
- `GITHUB_CLIENT_SECRET` - GitHub OAuth secret
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins

## Architecture

### Agent System
The backend uses CrewAI for multi-agent orchestration:

1. **Strategy Agent** - Analyzes project ideas and creates product strategy
2. **Architecture Agent** - Designs system architecture
3. **Code Builder Agent** - Generates code
4. **GitHub Agent** - Manages GitHub integration
5. **Pitch Agent** - Creates pitch materials

### Real-time Updates
WebSocket connections provide live updates during orchestration:
- Agent start/stop events
- Progress updates
- Generated outputs
- Error notifications

## Deployment

### Docker
```bash
docker build -t orkstrai-backend .
docker run -p 8000:8000 orkstrai-backend
```

### Railway/Render
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists

### watsonx API Errors
- Verify API key is valid
- Check project ID
- Ensure sufficient quota

### WebSocket Connection Fails
- Check CORS settings
- Verify WebSocket URL
- Check firewall rules