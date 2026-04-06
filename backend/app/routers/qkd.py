from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ..core.database import get_db
from ..core.rate_limit import simulation_rate_limit
from ..services.qkd_service import qkd_service
from ..services.auth_service import require_roles
from ..models import User
from ..websockets.manager import manager
from ..schemas import QKDRunRequest, QKDRunResponse, QKDSessionInfoResponse, QKDSystemStatsResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=QKDRunResponse)
async def run_qkd_protocol(
    payload: QKDRunRequest,
    request: Request,
    current_user: User = Depends(require_roles("admin", "user")),
):
    """Run the BB84 QKD protocol with given parameters."""
    simulation_rate_limit(request)
    try:
        parameters = payload.dict()
        logger.info("Starting QKD protocol for user=%s with parameters=%s", current_user.username, parameters)

        result = await qkd_service.run_bb84_protocol(parameters, user_id=current_user.id)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])

        await manager.send_qkd_result(result["session_id"], result)

        logger.info("QKD protocol completed successfully for session %s", result["session_id"])

        return QKDRunResponse(**result)

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error running QKD protocol")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session/{session_id}", response_model=QKDSessionInfoResponse)
async def get_qkd_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "user")),
):
    """Get QKD session details by session ID."""
    try:
        return {
            "session_id": session_id,
            "status": "completed",
            "message": "Session details would be retrieved from database",
            "requested_by": current_user.username,
        }
    except Exception:
        logger.exception("Error retrieving QKD session %s", session_id)
        raise HTTPException(status_code=500, detail="Error retrieving session")


@router.get("/stats", response_model=QKDSystemStatsResponse)
async def get_qkd_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "user")),
):
    """Get QKD system statistics."""
    try:
        return {
            "total_sessions": 0,
            "successful_sessions": 0,
            "average_key_length": 0,
            "average_error_rate": 0.0,
            "security_incidents": 0,
            "requested_by": current_user.username,
        }
    except Exception:
        logger.exception("Error retrieving QKD statistics")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


@router.websocket("/ws")
async def qkd_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time QKD updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
