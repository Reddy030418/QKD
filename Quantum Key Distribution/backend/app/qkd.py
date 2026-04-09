from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .core.database import db
from .services.qkd_service import qkd_service
import logging

qkd_bp = Blueprint('qkd', __name__)
logger = logging.getLogger(__name__)

@qkd_bp.route('/run', methods=['POST'])
# @jwt_required()
def run_qkd_protocol():
    """Run the BB84 QKD protocol with given parameters"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate parameters
        key_length = data.get('key_length', 50)
        noise_level = data.get('noise_level', 5.0)
        detector_efficiency = data.get('detector_efficiency', 95.0)
        eavesdropper_present = data.get('eavesdropper_present', False)

        # Validate parameter ranges
        if not (10 <= key_length <= 500):
            return jsonify({'error': 'Key length must be between 10 and 500'}), 400

        if not (0 <= noise_level <= 30):
            return jsonify({'error': 'Noise level must be between 0 and 30'}), 400

        if not (70 <= detector_efficiency <= 100):
            return jsonify({'error': 'Detector efficiency must be between 70 and 100'}), 400

        logger.info(f"Starting QKD protocol with parameters: {data}")

        # Run the QKD protocol
        result = qkd_service.run_bb84_protocol(data)

        if result['status'] == 'error':
            return jsonify({'error': result['error']}), 500

        logger.info(f"QKD protocol completed successfully for session {result['session_id']}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error running QKD protocol: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@qkd_bp.route('/session/<session_id>', methods=['GET'])
def get_qkd_session(session_id):
    """Get QKD session details by session ID"""
    try:
        # This would typically query the database for session details
        # For now, return a placeholder response
        return jsonify({
            'session_id': session_id,
            'status': 'completed',
            'message': 'Session details would be retrieved from database'
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving QKD session {session_id}: {e}")
        return jsonify({'error': f'Error retrieving session: {str(e)}'}), 500

@qkd_bp.route('/stats', methods=['GET'])
def get_qkd_stats():
    """Get QKD system statistics"""
    try:
        # This would typically query the database for statistics
        # For now, return placeholder statistics
        return jsonify({
            'total_sessions': 0,
            'successful_sessions': 0,
            'average_key_length': 0,
            'average_error_rate': 0.0,
            'security_incidents': 0
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving QKD statistics: {e}")
        return jsonify({'error': f'Error retrieving statistics: {str(e)}'}), 500
