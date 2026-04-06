from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from ..core.database import get_db
from ..core.audit import log_audit_event
from ..models import QKDSession, QKDSessionLog, User
from ..services.auth_service import require_admin, require_roles
from ..schemas import (
    SessionListItem,
    SessionDetailResponse,
    SessionSummaryStatsResponse,
    DeleteSessionResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _ensure_owner_or_admin(session: QKDSession, current_user: User):
    if current_user.role == "admin":
        return
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")


@router.get("/stats/summary", response_model=SessionSummaryStatsResponse)
async def get_session_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "user")),
):
    """Get summary statistics for sessions (global for admin, self for user)."""
    try:
        base_query = db.query(QKDSession)
        if current_user.role != "admin":
            base_query = base_query.filter(QKDSession.user_id == current_user.id)

        total_sessions = base_query.count()

        successful_sessions = base_query.filter(
            QKDSession.status == "completed",
            QKDSession.security_status == "secure"
        ).count()

        compromised_sessions = base_query.filter(
            QKDSession.security_status == "compromised"
        ).count()

        avg_result = base_query.with_entities(
            QKDSession.quantum_error_rate,
            QKDSession.final_key_length
        ).filter(QKDSession.status == "completed").all()

        avg_error_rate = 0.0
        avg_key_length = 0.0

        if avg_result:
            error_rates = [r[0] for r in avg_result if r[0] is not None]
            key_lengths = [r[1] for r in avg_result if r[1] is not None]
            avg_error_rate = sum(error_rates) / len(error_rates) if error_rates else 0.0
            avg_key_length = sum(key_lengths) / len(key_lengths) if key_lengths else 0.0

        tp = base_query.filter(
            QKDSession.eavesdropper_present.is_(False),
            QKDSession.security_status == "secure"
        ).count()
        fp = base_query.filter(
            QKDSession.eavesdropper_present.is_(True),
            QKDSession.security_status == "secure"
        ).count()
        tn = base_query.filter(
            QKDSession.eavesdropper_present.is_(True),
            QKDSession.security_status == "compromised"
        ).count()
        fn = base_query.filter(
            QKDSession.eavesdropper_present.is_(False),
            QKDSession.security_status == "compromised"
        ).count()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "compromised_sessions": compromised_sessions,
            "success_rate": (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "compromise_rate": (compromised_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "average_error_rate": round(avg_error_rate, 2),
            "average_key_length": round(avg_key_length, 2),
            "confusion_matrix": {
                "true_positive": tp,
                "false_positive": fp,
                "true_negative": tn,
                "false_negative": fn,
            },
            "f1_score": round(f1_score, 3),
        }

    except Exception:
        logger.exception("Error retrieving session statistics")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


@router.get("/", response_model=List[SessionListItem])
async def get_all_sessions(
    skip: int = 0,
    limit: int = 100,
    user_id: int = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "user")),
):
    """Get sessions. Users can see own sessions, admins can see all or filter by user_id."""
    try:
        query = db.query(QKDSession)

        if user_id is not None and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Cross-user queries require admin access")

        if current_user.role == "admin":
            if user_id is not None:
                query = query.filter(QKDSession.user_id == user_id)
                log_audit_event(
                    "sessions.cross_user_query",
                    actor=current_user,
                    target=f"user_id:{user_id}",
                    outcome="success",
                )
        else:
            query = query.filter(QKDSession.user_id == current_user.id)

        sessions = query.order_by(QKDSession.created_at.desc()).offset(skip).limit(limit).all()

        return [
            {
                "id": session.id,
                "session_id": session.session_id,
                "user_id": session.user_id,
                "key_length": session.key_length,
                "noise_level": session.noise_level,
                "detector_efficiency": session.detector_efficiency,
                "eavesdropper_present": session.eavesdropper_present,
                "transmitted_photons": session.transmitted_photons,
                "detected_photons": session.detected_photons,
                "quantum_error_rate": session.quantum_error_rate,
                "final_key_length": session.final_key_length,
                "status": session.status,
                "security_status": session.security_status,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            }
            for session in sessions
        ]

    except Exception:
        logger.exception("Error retrieving sessions")
        raise HTTPException(status_code=500, detail="Error retrieving sessions")


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "user")),
):
    """Get a specific QKD session by session ID with owner/admin access control."""
    try:
        session = db.query(QKDSession).filter(QKDSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        _ensure_owner_or_admin(session, current_user)

        logs = db.query(QKDSessionLog).filter(QKDSessionLog.session_id == session_id).all()

        return {
            "id": session.id,
            "session_id": session.session_id,
            "user_id": session.user_id,
            "key_length": session.key_length,
            "noise_level": session.noise_level,
            "detector_efficiency": session.detector_efficiency,
            "eavesdropper_present": session.eavesdropper_present,
            "alice_bits": session.alice_bits,
            "alice_bases": session.alice_bases,
            "bob_bases": session.bob_bases,
            "bob_measurements": session.bob_measurements,
            "sifted_key_alice": session.sifted_key_alice,
            "sifted_key_bob": session.sifted_key_bob,
            "final_shared_key": session.final_shared_key,
            "transmitted_photons": session.transmitted_photons,
            "detected_photons": session.detected_photons,
            "quantum_error_rate": session.quantum_error_rate,
            "final_key_length": session.final_key_length,
            "status": session.status,
            "security_status": session.security_status,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "level": log.level,
                    "message": log.message,
                    "data": log.data,
                }
                for log in logs
            ],
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error retrieving session %s", session_id)
        raise HTTPException(status_code=500, detail="Error retrieving session")


@router.delete("/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a QKD session (admin only)."""
    try:
        session = db.query(QKDSession).filter(QKDSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        db.query(QKDSessionLog).filter(QKDSessionLog.session_id == session_id).delete()
        db.delete(session)
        db.commit()

        logger.info("Session %s deleted successfully by user=%s", session_id, current_user.username)
        log_audit_event(
            "sessions.delete",
            actor=current_user,
            target=f"session_id:{session_id}",
            outcome="success",
        )

        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error deleting session %s", session_id)
        log_audit_event(
            "sessions.delete",
            actor=current_user,
            target=f"session_id:{session_id}",
            outcome="failure",
            reason="internal_error",
        )
        raise HTTPException(status_code=500, detail="Error deleting session")
