import json
import asyncio
import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket connection manager for real-time QKD updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

            # Remove from session-specific connections
            for session_id, connections in self.session_connections.items():
                if websocket in connections:
                    connections.remove(websocket)
                    if not connections:
                        del self.session_connections[session_id]
                    break

        logger.info(f"WebSocket connection closed. Remaining connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """Broadcast a message to all active connections"""
        disconnected_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected_connections.append(connection)

        # Clean up disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)

    async def broadcast_to_session(self, session_id: str, message: str):
        """Broadcast a message to connections subscribed to a specific session"""
        if session_id in self.session_connections:
            disconnected_connections = []

            for connection in self.session_connections[session_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to session {session_id}: {e}")
                    disconnected_connections.append(connection)

            # Clean up disconnected connections
            for connection in disconnected_connections:
                self.disconnect(connection)

    async def subscribe_to_session(self, websocket: WebSocket, session_id: str):
        """Subscribe a WebSocket connection to a specific session"""
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []

        if websocket not in self.session_connections[session_id]:
            self.session_connections[session_id].append(websocket)
            logger.info(f"WebSocket subscribed to session {session_id}")

    async def unsubscribe_from_session(self, websocket: WebSocket, session_id: str):
        """Unsubscribe a WebSocket connection from a specific session"""
        if session_id in self.session_connections and websocket in self.session_connections[session_id]:
            self.session_connections[session_id].remove(websocket)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
            logger.info(f"WebSocket unsubscribed from session {session_id}")

    async def handle_message(self, websocket: WebSocket, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get('type')

            if message_type == 'subscribe':
                session_id = data.get('session_id')
                if session_id:
                    await self.subscribe_to_session(websocket, session_id)
                    await self.send_personal_message(
                        json.dumps({
                            'type': 'subscribed',
                            'session_id': session_id,
                            'message': f'Subscribed to session {session_id}'
                        }),
                        websocket
                    )

            elif message_type == 'unsubscribe':
                session_id = data.get('session_id')
                if session_id:
                    await self.unsubscribe_from_session(websocket, session_id)
                    await self.send_personal_message(
                        json.dumps({
                            'type': 'unsubscribed',
                            'session_id': session_id,
                            'message': f'Unsubscribed from session {session_id}'
                        }),
                        websocket
                    )

            elif message_type == 'ping':
                await self.send_personal_message(
                    json.dumps({
                        'type': 'pong',
                        'timestamp': data.get('timestamp')
                    }),
                    websocket
                )

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
            await self.send_personal_message(
                json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }),
                websocket
            )
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_personal_message(
                json.dumps({
                    'type': 'error',
                    'message': 'Internal server error'
                }),
                websocket
            )

    async def broadcast_status(self):
        """Broadcast server status periodically"""
        while True:
            try:
                status_message = json.dumps({
                    'type': 'status',
                    'active_connections': len(self.active_connections),
                    'active_sessions': len(self.session_connections),
                    'timestamp': asyncio.get_event_loop().time()
                })

                await self.broadcast(status_message)

                # Wait for 30 seconds before next status update
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error broadcasting status: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def send_qkd_update(self, session_id: str, update_type: str, data: Dict[str, Any]):
        """Send QKD protocol update to subscribed connections"""
        message = json.dumps({
            'type': 'qkd_update',
            'session_id': session_id,
            'update_type': update_type,
            'data': data,
            'timestamp': asyncio.get_event_loop().time()
        })

        await self.broadcast_to_session(session_id, message)

    async def send_qkd_progress(self, session_id: str, step: str, progress: int, details: Dict[str, Any] = None):
        """Send QKD protocol progress update"""
        message = json.dumps({
            'type': 'qkd_progress',
            'session_id': session_id,
            'step': step,
            'progress': progress,
            'details': details or {},
            'timestamp': asyncio.get_event_loop().time()
        })

        await self.broadcast_to_session(session_id, message)

    async def send_qkd_result(self, session_id: str, result: Dict[str, Any]):
        """Send QKD protocol final result"""
        message = json.dumps({
            'type': 'qkd_result',
            'session_id': session_id,
            'result': result,
            'timestamp': asyncio.get_event_loop().time()
        })

        await self.broadcast_to_session(session_id, message)

# Global connection manager instance
manager = ConnectionManager()
