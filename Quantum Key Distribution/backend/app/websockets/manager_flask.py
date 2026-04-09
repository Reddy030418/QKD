import json
import logging
from typing import Dict, Any
from flask_socketio import SocketIO, emit, join_room, leave_room
from ..core.database import db

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket connection manager for real-time QKD updates and chat"""

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.chat_rooms: Dict[str, list] = {}

    def join_chat_room(self, room: str, sid: str):
        """Join a chat room"""
        if room not in self.chat_rooms:
            self.chat_rooms[room] = []
        if sid not in self.chat_rooms[room]:
            self.chat_rooms[room].append(sid)
            logger.info(f"Client {sid} joined chat room: {room}")

    def leave_chat_room(self, room: str, sid: str):
        """Leave a chat room"""
        if room in self.chat_rooms and sid in self.chat_rooms[room]:
            self.chat_rooms[room].remove(sid)
            if not self.chat_rooms[room]:
                del self.chat_rooms[room]
            logger.info(f"Client {sid} left chat room: {room}")

    def broadcast_to_room(self, room: str, event: str, data: Dict[str, Any]):
        """Broadcast message to a specific room"""
        socketio = SocketIO.get_instance()
        if socketio:
            socketio.emit(event, data, room=room)

    def broadcast_to_session(self, session_id: str, event: str, data: Dict[str, Any]):
        """Broadcast message to session subscribers"""
        if session_id in self.active_sessions:
            socketio = SocketIO.get_instance()
            if socketio:
                socketio.emit(event, data, room=session_id)

    def start_qkd_session(self, session_id: str, parameters: Dict[str, Any]):
        """Start tracking a QKD session"""
        self.active_sessions[session_id] = {
            'parameters': parameters,
            'status': 'running',
            'progress': 0,
            'start_time': json.dumps(parameters)  # Store as JSON string
        }
        logger.info(f"QKD session started: {session_id}")

    def update_qkd_progress(self, session_id: str, progress: int, step: str, details: Dict[str, Any] = None):
        """Update QKD session progress"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].update({
                'progress': progress,
                'current_step': step,
                'details': details or {}
            })

            # Broadcast progress update
            self.broadcast_to_session(session_id, 'qkd_progress', {
                'session_id': session_id,
                'progress': progress,
                'step': step,
                'details': details or {}
            })

    def complete_qkd_session(self, session_id: str, result: Dict[str, Any]):
        """Complete a QKD session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].update({
                'status': 'completed',
                'result': result,
                'completed_at': json.dumps(result)
            })

            # Broadcast completion
            self.broadcast_to_session(session_id, 'qkd_result', {
                'session_id': session_id,
                'result': result
            })

            logger.info(f"QKD session completed: {session_id}")

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of a QKD session"""
        return self.active_sessions.get(session_id, {})

    def get_active_sessions_count(self) -> int:
        """Get count of active QKD sessions"""
        return len(self.active_sessions)

    def get_chat_rooms_count(self) -> int:
        """Get count of active chat rooms"""
        return len(self.chat_rooms)

# Global connection manager instance
manager = ConnectionManager()
