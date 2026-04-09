from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ..core.database import get_db
from ..services.qkd_service import qkd_service
from ..websockets.manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=Dict[str, Any])
async def run_qkd_protocol(
    parameters: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Run the BB84 QKD protocol with given parameters"""
    try:
        # Validate parameters
        key_length = parameters.get('key_length', 50)
        noise_level = parameters.get('noise_level', 5.0)
        detector_efficiency = parameters.get('detector_efficiency', 95.0)
        eavesdropper_present = parameters.get('eavesdropper_present', False)

        # Validate parameter ranges
        if not (10 <= key_length <= 500):
            raise HTTPException(status_code=400, detail="Key length must be between 10 and 500")

        if not (0 <= noise_level <= 30):
            raise HTTPException(status_code=400, detail="Noise level must be between 0 and 30")

        if not (70 <= detector_efficiency <= 100):
            raise HTTPException(status_code=400, detail="Detector efficiency must be between 70 and 100")

        logger.info(f"Starting QKD protocol with parameters: {parameters}")

        # Run the QKD protocol
        result = await qkd_service.run_bb84_protocol(parameters)

        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error'])

        # Send real-time updates via WebSocket
        await manager.send_qkd_result(result['session_id'], result)

        logger.info(f"QKD protocol completed successfully for session {result['session_id']}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running QKD protocol: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/session/{session_id}", response_model=Dict[str, Any])
async def get_qkd_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get QKD session details by session ID"""
    try:
        # This would typically query the database for session details
        # For now, return a placeholder response
        return {
            'session_id': session_id,
            'status': 'completed',
            'message': 'Session details would be retrieved from database'
        }
    except Exception as e:
        logger.error(f"Error retrieving QKD session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_qkd_stats(db: Session = Depends(get_db)):
    """Get QKD system statistics"""
    try:
        # This would typically query the database for statistics
        # For now, return placeholder statistics
        return {
            'total_sessions': 0,
            'successful_sessions': 0,
            'average_key_length': 0,
            'average_error_rate': 0.0,
            'security_incidents': 0
        }
    except Exception as e:
        logger.error(f"Error retrieving QKD statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@router.websocket("/ws")
async def qkd_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time QKD updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
