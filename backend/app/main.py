"""
OrkestrAI FastAPI Application Entry Point
"""
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.dependencies.rate_limiter import limiter
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.session import engine, get_db
from app.api.v1.router import api_router
from sqlalchemy import text
import structlog
import uuid
import hashlib

def redact_user_input(logger, log_method, event_dict):
    """Redact user_input field if present"""
    if "user_input" in event_dict and isinstance(event_dict["user_input"], str):
        # Truncated hash of the input for traceability without exposing content
        event_dict["user_input"] = f"[REDACTED] hash: {hashlib.sha256(event_dict['user_input'].encode()).hexdigest()[:8]}"
    return event_dict

# Setup structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        redact_user_input,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting OrkestrAI backend")
    # Base.metadata.create_all removed in favor of Alembic migrations
    
    yield
    
    # Shutdown
    logger.info("Shutting down OrkestrAI backend")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered multi-agent software development orchestration",
    version=settings.VERSION,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    structlog.contextvars.clear_contextvars()
    return response

# Configure CORS - whitelist origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(os.path.join(STATIC_DIR, "generated"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OrkestrAI API",
        "version": settings.VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "unhealthy"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        logger.error("Health check DB failure", error=str(e))
        
    # Check LLM router status
    llm_status = "healthy"
    # Note: providers are now created on-the-fly per user
        
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "llm_system": llm_status
    }

# Made with Bob
