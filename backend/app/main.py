from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import asyncio
import time
import uuid
from .core.config import settings
from .core.database import create_db_and_tables
from .core.logging_config import configure_logging
from .routers import qkd, auth, sessions, analytics
from .websockets.manager import ConnectionManager
import logging

configure_logging()
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
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response


app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-Request-ID"],
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "validation_error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "reason": "request_validation_failed",
        },
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request payload",
            "errors": exc.errors(),
        },
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(qkd.router, prefix="/qkd", tags=["quantum-key-distribution"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

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
        "version": settings.api_version
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
