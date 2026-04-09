from flask import Blueprint, request, jsonify
from .core.database import db
from .models.qkd_session import QKDSession, QKDSessionLog
import logging

sessions_bp = Blueprint('sessions', __name__)
logger = logging.getLogger(__name__)

@sessions_bp.route('/', methods=['GET'])
def get_all_sessions():
    """Get all QKD sessions"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)

        sessions = QKDSession.query.offset(skip).limit(limit).all()

        return jsonify([
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
        ]), 200

    except Exception as e:
        logger.error(f"Error retrieving sessions: {e}")
        return jsonify({'error': f'Error retrieving sessions: {str(e)}'}), 500

@sessions_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get a specific QKD session by session ID"""
    try:
        session = QKDSession.query.filter_by(session_id=session_id).first()

        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # Get session logs
        logs = QKDSessionLog.query.filter_by(session_id=session_id).all()

        return jsonify({
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
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {e}")
        return jsonify({'error': f'Error retrieving session: {str(e)}'}), 500

@sessions_bp.route('/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a QKD session"""
    try:
        session = QKDSession.query.filter_by(session_id=session_id).first()

        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # Delete associated logs first
        QKDSessionLog.query.filter_by(session_id=session_id).delete()

        # Delete the session
        db.session.delete(session)
        db.session.commit()

        logger.info(f"Session {session_id} deleted successfully")

        return jsonify({"message": "Session deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting session {session_id}: {e}")
        return jsonify({'error': f'Error deleting session: {str(e)}'}), 500

@sessions_bp.route('/stats/summary', methods=['GET'])
def get_session_stats():
    """Get summary statistics for all QKD sessions"""
    try:
        # Get total sessions
        total_sessions = QKDSession.query.count()

        # Get successful sessions (completed status)
        successful_sessions = QKDSession.query.filter_by(status='completed').count()

        # Get compromised sessions
        compromised_sessions = QKDSession.query.filter_by(security_status='compromised').count()

        # Calculate averages
        avg_result = QKDSession.query.with_entities(
            QKDSession.quantum_error_rate,
            QKDSession.final_key_length
        ).filter_by(status='completed').all()

        avg_error_rate = 0.0
        avg_key_length = 0

        if avg_result:
            error_rates = [r[0] for r in avg_result if r[0] is not None]
            key_lengths = [r[1] for r in avg_result if r[1] is not None]

            avg_error_rate = sum(error_rates) / len(error_rates) if error_rates else 0.0
            avg_key_length = sum(key_lengths) / len(key_lengths) if key_lengths else 0

        return jsonify({
            'total_sessions': total_sessions,
            'successful_sessions': successful_sessions,
            'compromised_sessions': compromised_sessions,
            'success_rate': (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'compromise_rate': (compromised_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'average_error_rate': round(avg_error_rate, 2),
            'average_key_length': round(avg_key_length, 2)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving session statistics: {e}")
        return jsonify({'error': f'Error retrieving statistics: {str(e)}'}), 500
