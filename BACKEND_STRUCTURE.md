# OrkestrAI - Backend Architecture & Structure

## Backend Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration management
│   ├── dependencies.py              # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py            # Main API router
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── projects.py      # Project CRUD endpoints
│   │   │   │   ├── orchestration.py # Agent orchestration endpoints
│   │   │   │   ├── agents.py        # Agent status/logs endpoints
│   │   │   │   ├── github.py        # GitHub integration endpoints
│   │   │   │   └── websocket.py     # WebSocket connections
│   │   │   └── deps.py              # API dependencies
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base agent class
│   │   ├── orchestrator.py          # Main orchestration logic
│   │   ├── strategy_agent.py        # Product Strategy Agent
│   │   ├── architecture_agent.py    # Architecture Agent
│   │   ├── code_builder_agent.py    # Code Builder Agent
│   │   ├── github_agent.py          # GitHub Management Agent
│   │   ├── pitch_agent.py           # Pitch & Demo Agent
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── idea_analyzer.py
│   │       ├── feature_prioritizer.py
│   │       ├── tech_stack_recommender.py
│   │       ├── schema_designer.py
│   │       ├── code_generator.py
│   │       └── github_client.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py              # Authentication & authorization
│   │   ├── logging.py               # Structured logging setup
│   │   ├── events.py                # Event system for real-time updates
│   │   └── exceptions.py            # Custom exceptions
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                  # SQLAlchemy base
│   │   ├── session.py               # Database session management
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── project.py           # Project model
│   │       ├── agent_log.py         # Agent execution logs
│   │       ├── generated_artifact.py # Generated code/docs
│   │       └── user.py              # User model (future)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── project.py               # Pydantic schemas for projects
│   │   ├── agent.py                 # Agent-related schemas
│   │   ├── orchestration.py         # Orchestration request/response
│   │   └── github.py                # GitHub integration schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── project_service.py       # Business logic for projects
│   │   ├── orchestration_service.py # Orchestration coordination
│   │   ├── github_service.py        # GitHub API integration
│   │   └── websocket_service.py     # WebSocket event broadcasting
│   │
│   └── utils/
│       ├── __init__.py
│       ├── code_formatter.py        # Code formatting utilities
│       ├── file_generator.py        # File/ZIP generation
│       └── validators.py            # Input validation helpers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_api/
│   ├── test_agents/
│   └── test_services/
│
├── alembic/                         # Database migrations
│   ├── versions/
│   └── env.py
│
├── .env.example                     # Environment variables template
├── .gitignore
├── alembic.ini                      # Alembic configuration
├── requirements.txt                 # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## API Routes Planning

### Base URL: `/api/v1`

### 1. Projects Endpoints

```python
# Create new project and start orchestration
POST /api/v1/projects
Request Body:
{
  "name": "My Hackathon App",
  "description": "A social platform for developers",
  "user_input": "I want to build a social network for developers...",
  "preferences": {
    "tech_stack": ["Next.js", "FastAPI"],  # Optional
    "deployment": "Vercel",                 # Optional
    "include_auth": true                    # Optional
  }
}
Response: 201 Created
{
  "project_id": "uuid",
  "name": "My Hackathon App",
  "status": "orchestrating",
  "created_at": "2026-05-15T17:30:00Z",
  "websocket_url": "ws://localhost:8000/ws/orchestration/uuid"
}

# Get project details
GET /api/v1/projects/{project_id}
Response: 200 OK
{
  "project_id": "uuid",
  "name": "string",
  "status": "completed|orchestrating|failed",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "outputs": {
    "strategy": {...},
    "architecture": {...},
    "code": {...},
    "github": {...},
    "pitch": {...}
  }
}

# List all projects
GET /api/v1/projects?limit=10&offset=0
Response: 200 OK
{
  "projects": [...],
  "total": 42,
  "limit": 10,
  "offset": 0
}

# Delete project
DELETE /api/v1/projects/{project_id}
Response: 204 No Content
```

### 2. Orchestration Endpoints

```python
# Get orchestration status
GET /api/v1/orchestration/{project_id}/status
Response: 200 OK
{
  "project_id": "uuid",
  "status": "orchestrating",
  "current_agent": "ArchitectureAgent",
  "progress": 60,
  "completed_agents": ["ProductStrategyAgent"],
  "remaining_agents": ["CodeBuilderAgent", "GitHubAgent", "PitchAgent"],
  "estimated_completion": "2026-05-15T17:35:00Z"
}

# Get agent execution logs
GET /api/v1/orchestration/{project_id}/logs?agent=all
Response: 200 OK
{
  "logs": [
    {
      "id": "uuid",
      "agent_name": "ProductStrategyAgent",
      "action": "Analyzing project requirements",
      "status": "completed",
      "timestamp": "2026-05-15T17:30:00Z",
      "duration_ms": 2500,
      "output_preview": "Identified 5 core features..."
    }
  ]
}

# Retry failed orchestration
POST /api/v1/orchestration/{project_id}/retry
Response: 200 OK
{
  "message": "Orchestration restarted",
  "project_id": "uuid"
}
```

### 3. Agent Endpoints

```python
# Get available agents
GET /api/v1/agents
Response: 200 OK
{
  "agents": [
    {
      "name": "ProductStrategyAgent",
      "role": "Product Manager",
      "description": "Analyzes ideas and creates product strategy",
      "status": "active"
    }
  ]
}

# Get specific agent details
GET /api/v1/agents/{agent_name}
Response: 200 OK
{
  "name": "ProductStrategyAgent",
  "role": "Product Manager",
  "capabilities": ["idea_analysis", "feature_prioritization"],
  "tools": ["idea_analyzer", "feature_prioritizer"],
  "average_execution_time_ms": 3000
}
```

### 4. Artifacts Endpoints

```python
# Download generated code as ZIP
GET /api/v1/projects/{project_id}/artifacts/code/download
Response: 200 OK (application/zip)

# Get specific artifact
GET /api/v1/projects/{project_id}/artifacts/{artifact_type}
# artifact_type: strategy|architecture|code|github|pitch
Response: 200 OK
{
  "artifact_type": "code",
  "content": {...},
  "generated_at": "timestamp",
  "files": [
    {
      "path": "src/app.py",
      "content": "...",
      "language": "python"
    }
  ]
}

# Get architecture diagram
GET /api/v1/projects/{project_id}/artifacts/architecture/diagram
Response: 200 OK
{
  "diagram_type": "mermaid",
  "content": "graph TD\n  A --> B"
}
```

### 5. GitHub Integration Endpoints

```python
# Connect GitHub account (OAuth)
GET /api/v1/github/auth
Response: 302 Redirect to GitHub OAuth

# GitHub OAuth callback
GET /api/v1/github/callback?code=xxx
Response: 200 OK
{
  "access_token": "encrypted_token",
  "username": "github_username"
}

# Create GitHub repository from project
POST /api/v1/projects/{project_id}/github/create-repo
Request Body:
{
  "repo_name": "my-hackathon-app",
  "private": false,
  "create_issues": true,
  "push_code": true
}
Response: 201 Created
{
  "repo_url": "https://github.com/user/my-hackathon-app",
  "issues_created": 12,
  "initial_commit": "abc123"
}

# Get GitHub integration status
GET /api/v1/projects/{project_id}/github/status
Response: 200 OK
{
  "connected": true,
  "repo_url": "https://github.com/user/repo",
  "issues_count": 12,
  "last_sync": "timestamp"
}
```

### 6. WebSocket Endpoint

```python
# Real-time orchestration updates
WS /ws/orchestration/{project_id}

# Client receives events:
{
  "type": "agent_start",
  "agent": "ProductStrategyAgent",
  "timestamp": "2026-05-15T17:30:00Z"
}

{
  "type": "agent_thinking",
  "agent": "ProductStrategyAgent",
  "message": "Analyzing target users...",
  "timestamp": "2026-05-15T17:30:02Z"
}

{
  "type": "agent_output",
  "agent": "ProductStrategyAgent",
  "data": {
    "features": [...],
    "mvp_scope": [...]
  },
  "timestamp": "2026-05-15T17:30:05Z"
}

{
  "type": "agent_complete",
  "agent": "ProductStrategyAgent",
  "duration_ms": 5000,
  "timestamp": "2026-05-15T17:30:05Z"
}

{
  "type": "orchestration_complete",
  "project_id": "uuid",
  "timestamp": "2026-05-15T17:35:00Z"
}

{
  "type": "error",
  "agent": "CodeBuilderAgent",
  "error": "Failed to generate code",
  "details": "...",
  "timestamp": "2026-05-15T17:32:00Z"
}
```

### 7. Health & Monitoring Endpoints

```python
# Health check
GET /api/v1/health
Response: 200 OK
{
  "status": "healthy",
  "database": "connected",
  "watsonx_api": "available",
  "version": "1.0.0"
}

# Metrics
GET /api/v1/metrics
Response: 200 OK
{
  "total_projects": 150,
  "active_orchestrations": 3,
  "average_completion_time_ms": 45000,
  "success_rate": 0.95
}
```

## Database Schema

### PostgreSQL Schema Design

```sql
-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_input TEXT NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'orchestrating', 'completed', 'failed'
    preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- Agent execution logs
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    action TEXT NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'started', 'thinking', 'completed', 'failed'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    output_preview TEXT,
    full_output JSONB,
    error_details TEXT,
    metadata JSONB
);

-- Generated artifacts
CREATE TABLE generated_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL, -- 'strategy', 'architecture', 'code', 'github', 'pitch'
    content JSONB NOT NULL,
    generated_by VARCHAR(100) NOT NULL, -- Agent name
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_count INTEGER,
    total_size_bytes INTEGER
);

-- GitHub integrations
CREATE TABLE github_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    repo_url VARCHAR(500),
    repo_name VARCHAR(255),
    issues_created INTEGER DEFAULT 0,
    initial_commit_sha VARCHAR(40),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_at TIMESTAMP WITH TIME ZONE
);

-- Users table (for future authentication)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    github_username VARCHAR(255),
    github_access_token TEXT, -- Encrypted
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_agent_logs_project_id ON agent_logs(project_id);
CREATE INDEX idx_agent_logs_agent_name ON agent_logs(agent_name);
CREATE INDEX idx_artifacts_project_id ON generated_artifacts(project_id);
CREATE INDEX idx_artifacts_type ON generated_artifacts(artifact_type);
```

## Key Backend Components

### 1. Main Application Entry Point

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.db.session import engine
from app.db.base import Base

app = FastAPI(
    title="OrkestrAI API",
    description="AI-powered multi-agent software development orchestration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
setup_logging()

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Create database tables
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "OrkestrAI API", "version": "1.0.0"}
```

### 2. Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OrkestrAI"
    
    # Database
    DATABASE_URL: str
    
    # IBM watsonx
    WATSONX_API_KEY: str
    WATSONX_PROJECT_ID: str
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    
    # GitHub
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Orchestration Service

```python
# app/services/orchestration_service.py
from app.agents.orchestrator import OrkestrAICrew
from app.services.websocket_service import WebSocketManager
from app.db.models.project import Project
from app.db.models.agent_log import AgentLog

class OrchestrationService:
    def __init__(self):
        self.crew = OrkestrAICrew()
        self.ws_manager = WebSocketManager()
    
    async def start_orchestration(self, project: Project):
        """Start the multi-agent orchestration process"""
        try:
            # Broadcast start event
            await self.ws_manager.broadcast(
                project.id,
                {"type": "orchestration_start", "project_id": str(project.id)}
            )
            
            # Run CrewAI orchestration
            result = await self.crew.run_orchestration(
                user_input=project.user_input,
                project_id=project.id,
                preferences=project.preferences,
                event_callback=self._handle_agent_event
            )
            
            # Update project status
            project.status = "completed"
            project.completed_at = datetime.utcnow()
            
            # Broadcast completion
            await self.ws_manager.broadcast(
                project.id,
                {"type": "orchestration_complete", "project_id": str(project.id)}
            )
            
            return result
            
        except Exception as e:
            project.status = "failed"
            project.error_message = str(e)
            await self.ws_manager.broadcast(
                project.id,
                {"type": "error", "error": str(e)}
            )
            raise
    
    async def _handle_agent_event(self, event: dict):
        """Handle agent events and broadcast to WebSocket clients"""
        await self.ws_manager.broadcast(event["project_id"], event)
```

## Technology Stack Details

### Core Dependencies

```txt
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0

# AI & Agents
crewai==0.1.0
ibm-watsonx-ai==0.1.0
langchain==0.1.0

# GitHub Integration
PyGithub==2.1.1

# WebSocket
python-socketio==5.10.0
websockets==12.0

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6
structlog==24.1.0
httpx==0.26.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
```

## Development Workflow

### Local Development Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env with your credentials

# 4. Run database migrations
alembic upgrade head

# 5. Start development server
uvicorn app.main:app --reload --port 8000
```

### Docker Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/orkstrai
    depends_on:
      - db
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=orkstrai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data: