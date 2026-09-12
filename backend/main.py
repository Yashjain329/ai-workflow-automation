import os
import asyncio
import json
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import Base, engine
# Import all models to ensure they are registered with Base before creating tables
from backend.models import db_models, monitoring_models
from backend.api import jobs, approvals, metrics, monitoring
from backend.auth import get_api_key, get_current_user, require_read, require_write, require_approve

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="End-to-End AI-Based Intelligent Workflow Automation Platform"
    # No global dependencies here
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with authentication dependencies
# We'll apply the get_api_key dependency to all routes in these routers
app.include_router(jobs.router, prefix=settings.API_PREFIX, dependencies=[Depends(get_api_key)])
app.include_router(approvals.router, prefix=settings.API_PREFIX, dependencies=[Depends(get_api_key)])
app.include_router(metrics.router, prefix=settings.API_PREFIX, dependencies=[Depends(get_api_key)])
app.include_router(monitoring.router, prefix=settings.API_PREFIX, dependencies=[Depends(get_api_key)])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Background task to broadcast updates every 10 seconds
async def broadcast_periodic_updates():
    while True:
        await asyncio.sleep(10)  # Send update every 10 seconds
        if manager.active_connections:  # Only broadcast if there are connected clients
            await manager.broadcast(json.dumps({"type": "update"}))

@app.on_event("startup")
async def startup_event():
    # Start the background task for broadcasting updates
    asyncio.create_task(broadcast_periodic_updates())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We'll keep the connection alive by waiting for any messages from the client
            # If we receive a message, we can echo it back or handle it
            # But for now, we just wait to detect disconnections
            data = await websocket.receive_text()
            # Optionally, we can echo the message back
            await manager.send_personal_message(f"Message text was: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Serve Frontend static directory if exists
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_dashboard():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to AI-Based Intelligent Workflow Automation API", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}