from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from ..core.database import get_db
from ..models import QKDSession, QKDSessionLog

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all QKD sessions"""
    try:
        sessions = db.query(QKDSession).offset(skip).limit(limit).all()

        return [
            {
                'id': session.id,
                'session_id': session.session_id,
                'key_length': session.key_length,
                'noise_level': session.noise_level,
                'detector_efficiency': session.detector_efficiency,
                'eavesdropper_present': session.eavesdropper_present,
                'transmitted_photons': session.transmitted_photons,
                'detected_photons': session.detected_photons,
                'quantum_error_rate': session.quantum_error_rate,
                'final_key_length': session.final_key_length,
                'status': session.status,
                'security_status': session.security_status,
                'created_at': session.created_at.isoformat() if session.created_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None
            }
            for session in sessions
        ]

    except Exception as e:
        logger.error(f"Error retrieving sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

@router.get("/{session_id}", response_model=Dict[str, Any])
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific QKD session by session ID"""
    try:
        session = db.query(QKDSession).filter(QKDSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get session logs
        logs = db.query(QKDSessionLog).filter(QKDSessionLog.session_id == session_id).all()

        return {
            'id': session.id,
            'session_id': session.session_id,
            'key_length': session.key_length,
            'noise_level': session.noise_level,
            'detector_efficiency': session.detector_efficiency,
            'eavesdropper_present': session.eavesdropper_present,
            'alice_bits': session.alice_bits,
            'alice_bases': session.alice_bases,
            'bob_bases': session.bob_bases,
            'bob_measurements': session.bob_measurements,
            'sifted_key_alice': session.sifted_key_alice,
            'sifted_key_bob': session.sifted_key_bob,
            'final_shared_key': session.final_shared_key,
            'transmitted_photons': session.transmitted_photons,
            'detected_photons': session.detected_photons,
            'quantum_error_rate': session.quantum_error_rate,
            'final_key_length': session.final_key_length,
            'status': session.status,
            'security_status': session.security_status,
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'logs': [
                {
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                    'level': log.level,
                    'message': log.message,
                    'data': log.data
                }
                for log in logs
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a QKD session"""
    try:
        session = db.query(QKDSession).filter(QKDSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Delete associated logs first
        db.query(QKDSessionLog).filter(QKDSessionLog.session_id == session_id).delete()

        # Delete the session
        db.delete(session)
        db.commit()

        logger.info(f"Session {session_id} deleted successfully")

        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.get("/stats/summary", response_model=Dict[str, Any])
async def get_session_stats(db: Session = Depends(get_db)):
    """Get summary statistics for all QKD sessions"""
    try:
        # Get total sessions
        total_sessions = db.query(QKDSession).count()

        # Get successful sessions (completed and secure)
        successful_sessions = db.query(QKDSession).filter(
            QKDSession.status == 'completed',
            QKDSession.security_status == 'secure'
        ).count()

        # Get compromised sessions
        compromised_sessions = db.query(QKDSession).filter(
            QKDSession.security_status == 'compromised'
        ).count()

        # Calculate averages
        avg_result = db.query(
            QKDSession.quantum_error_rate,
            QKDSession.final_key_length
        ).filter(QKDSession.status == 'completed').all()

        avg_error_rate = 0.0
        avg_key_length = 0

        if avg_result:
            error_rates = [r[0] for r in avg_result if r[0] is not None]
            key_lengths = [r[1] for r in avg_result if r[1] is not None]

            avg_error_rate = sum(error_rates) / len(error_rates) if error_rates else 0.0
            avg_key_length = sum(key_lengths) / len(key_lengths) if key_lengths else 0

        # Calculate confusion matrix values based on QKD simulator classification
        # True Positive: Correctly identified as secure (no eavesdropper and detected as secure)
        tp = db.query(QKDSession).filter(
            QKDSession.eavesdropper_present == False,
            QKDSession.security_status == 'secure'
        ).count()

        # False Positive: Incorrectly identified as secure (eavesdropper present but detected as secure)
        fp = db.query(QKDSession).filter(
            QKDSession.eavesdropper_present == True,
            QKDSession.security_status == 'secure'
        ).count()

        # True Negative: Correctly identified as compromised (eavesdropper present and detected as compromised)
        tn = db.query(QKDSession).filter(
            QKDSession.eavesdropper_present == True,
            QKDSession.security_status == 'compromised'
        ).count()

        # False Negative: Incorrectly identified as compromised (no eavesdropper but detected as compromised)
        fn = db.query(QKDSession).filter(
            QKDSession.eavesdropper_present == False,
            QKDSession.security_status == 'compromised'
        ).count()

        # Calculate F1 Score
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            'total_sessions': total_sessions,
            'successful_sessions': successful_sessions,
            'compromised_sessions': compromised_sessions,
            'success_rate': (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'compromise_rate': (compromised_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'average_error_rate': round(avg_error_rate, 2),
            'average_key_length': round(avg_key_length, 2),
            'confusion_matrix': {
                'true_positive': tp,
                'false_positive': fp,
                'true_negative': tn,
                'false_negative': fn
            },
            'f1_score': round(f1_score, 3)
        }

    except Exception as e:
        logger.error(f"Error retrieving session statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
