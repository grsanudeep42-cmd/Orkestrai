"""
WebSocket endpoint for real-time orchestration updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import structlog
import json

logger = structlog.get_logger()

router = APIRouter()

# Store active WebSocket connections per project
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections"""
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        if project_id not in active_connections:
            active_connections[project_id] = set()
        active_connections[project_id].add(websocket)
        logger.info("WebSocket connected", project_id=project_id, 
                   total_connections=len(active_connections[project_id]))
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """Remove a WebSocket connection"""
        if project_id in active_connections:
            active_connections[project_id].discard(websocket)
            if not active_connections[project_id]:
                del active_connections[project_id]
        logger.info("WebSocket disconnected", project_id=project_id)
    
    async def broadcast(self, project_id: str, message: dict):
        """Broadcast a message to all connections for a project"""
        if project_id in active_connections:
            disconnected = set()
            for connection in active_connections[project_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("Failed to send message", error=str(e))
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                active_connections[project_id].discard(conn)
    
    async def broadcast_to_project(self, project_id: str, message: dict):
        """Alias for broadcast method for consistency"""
        await self.broadcast(project_id, message)


manager = ConnectionManager()


@router.websocket("/orchestration/{project_id}")
async def websocket_orchestration(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time orchestration updates
    
    Clients will receive events like:
    - agent_start: When an agent begins execution
    - agent_thinking: Progress updates from the agent
    - agent_output: When an agent produces output
    - agent_complete: When an agent finishes
    - orchestration_complete: When all agents finish
    - error: When an error occurs
    """
    await manager.connect(websocket, project_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "project_id": project_id,
            "message": "Connected to orchestration stream"
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for now (can be used for client commands later)
                await websocket.send_json({
                    "type": "echo",
                    "data": data
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("WebSocket error", error=str(e), project_id=project_id)
                break
    
    finally:
        manager.disconnect(websocket, project_id)


async def broadcast_event(project_id: str, event: dict):
    """
    Helper function to broadcast events to all connected clients
    Can be called from orchestration service
    """
    await manager.broadcast(project_id, event)

# Made with Bob
