from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from .core.config import settings
from .core.database import create_db_and_tables
from .routers import qkd, auth, sessions
from .websockets.manager import ConnectionManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection manager for WebSocket connections
manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting QKD Backend Server...")
    # Create database tables
    create_db_and_tables()
    logger.info("Database tables created successfully")

    # Start background tasks
    asyncio.create_task(manager.broadcast_status())

    yield

    logger.info("Shutting down QKD Backend Server...")

# Create FastAPI application
app = FastAPI(
    title="Quantum Key Distribution (BB84) API",
    description="Backend API for BB84 Quantum Key Distribution simulation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(qkd.router, prefix="/qkd", tags=["quantum-key-distribution"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

# WebSocket endpoint for real-time QKD simulation
@app.websocket("/ws/qkd")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages
            await manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "QKD Backend API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Quantum Key Distribution (BB84) API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
