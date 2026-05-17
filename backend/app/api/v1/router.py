"""
Main API v1 router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import projects, orchestration, websocket, auth

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(orchestration.router, prefix="/orchestration", tags=["orchestration"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# Made with Bob
