from ..core.database import db, get_db
from ..models import ChatRoom, ChatMessage, ChatParticipant, User, QKDSession
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ChatService:
    """Service for managing chat functionality"""

    @staticmethod
    def create_room(name: str, description: str, created_by: int,
                   room_type: str = 'general', session_id: Optional[int] = None) -> ChatRoom:
        """Create a new chat room"""
        try:
            room = ChatRoom(
                name=name,
                description=description,
                room_type=room_type,
                session_id=session_id,
                created_by=created_by
            )
            db.session.add(room)
            db.session.flush()  # Get the room ID

            # Add creator as admin participant
            participant = ChatParticipant(
                room_id=room.id,
                user_id=created_by,
                role='admin'
            )
            db.session.add(participant)
            db.session.commit()

            logger.info(f"Chat room '{name}' created by user {created_by}")
            return room
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating chat room: {e}")
            raise

    @staticmethod
    def get_room(room_id: int) -> Optional[ChatRoom]:
        """Get a chat room by ID"""
        return ChatRoom.query.get(room_id)

    @staticmethod
    def get_rooms_for_user(user_id: int) -> List[ChatRoom]:
        """Get all chat rooms a user is a participant in"""
        return ChatRoom.query.join(ChatParticipant).filter(
            ChatParticipant.user_id == user_id
        ).all()

    @staticmethod
    def get_session_room(session_id: int) -> Optional[ChatRoom]:
        """Get the chat room associated with a QKD session"""
        return ChatRoom.query.filter_by(session_id=session_id, room_type='qkd_session').first()

    @staticmethod
    def send_message(room_id: int, user_id: int, content: str,
                    message_type: str = 'text', metadata: Optional[Dict] = None) -> ChatMessage:
        """Send a message to a chat room"""
        try:
            message = ChatMessage(
                content=content,
                message_type=message_type,
                metadata=metadata,
                room_id=room_id,
                user_id=user_id
            )
            db.session.add(message)
            db.session.commit()

            logger.info(f"Message sent by user {user_id} in room {room_id}")
            return message
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sending message: {e}")
            raise

    @staticmethod
    def get_room_messages(room_id: int, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Get messages from a chat room"""
        return ChatMessage.query.filter_by(room_id=room_id)\
            .order_by(ChatMessage.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

    @staticmethod
    def add_participant(room_id: int, user_id: int, role: str = 'member') -> ChatParticipant:
        """Add a user to a chat room"""
        try:
            # Check if user is already a participant
            existing = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
            if existing:
                return existing

            participant = ChatParticipant(
                room_id=room_id,
                user_id=user_id,
                role=role
            )
            db.session.add(participant)
            db.session.commit()

            logger.info(f"User {user_id} added to room {room_id}")
            return participant
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding participant: {e}")
            raise

    @staticmethod
    def remove_participant(room_id: int, user_id: int) -> bool:
        """Remove a user from a chat room"""
        try:
            participant = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
            if participant:
                db.session.delete(participant)
                db.session.commit()
                logger.info(f"User {user_id} removed from room {room_id}")
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing participant: {e}")
            raise

    @staticmethod
    def get_room_participants(room_id: int) -> List[ChatParticipant]:
        """Get all participants in a chat room"""
        return ChatParticipant.query.filter_by(room_id=room_id).all()

    @staticmethod
    def create_session_room(session_id: int, created_by: int) -> ChatRoom:
        """Create a chat room for a QKD session"""
        try:
            session = QKDSession.query.get(session_id)
            if not session:
                raise ValueError(f"QKD session {session_id} not found")

            # Check if room already exists
            existing_room = ChatRoom.query.filter_by(session_id=session_id, room_type='qkd_session').first()
            if existing_room:
                return existing_room

            room_name = f"QKD Session {session.session_id}"
            room_description = f"Chat for QKD simulation session {session.session_id}"

            return ChatService.create_room(
                name=room_name,
                description=room_description,
                room_type='qkd_session',
                session_id=session_id,
                created_by=created_by
            )
        except Exception as e:
            logger.error(f"Error creating session room: {e}")
            raise

    @staticmethod
    def get_user_rooms_with_unread(user_id: int) -> List[Dict[str, Any]]:
        """Get user's rooms with unread message counts"""
        try:
            # This is a simplified version - in a real app you'd track read timestamps
            rooms = ChatService.get_rooms_for_user(user_id)
            result = []

            for room in rooms:
                message_count = ChatMessage.query.filter_by(room_id=room.id).count()
                result.append({
                    'room': room,
                    'message_count': message_count,
                    'last_message': ChatMessage.query.filter_by(room_id=room.id)\
                        .order_by(ChatMessage.created_at.desc()).first()
                })

            return result
        except Exception as e:
            logger.error(f"Error getting user rooms: {e}")
            raise

    @staticmethod
    def search_messages(room_id: int, query: str, limit: int = 20) -> List[ChatMessage]:
        """Search messages in a room"""
        return ChatMessage.query.filter(
            ChatMessage.room_id == room_id,
            ChatMessage.content.contains(query)
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    @staticmethod
    def delete_message(message_id: int, user_id: int) -> bool:
        """Delete a message (only by sender or admin)"""
        try:
            message = ChatMessage.query.get(message_id)
            if not message:
                return False

            # Check if user can delete (sender or admin of the room)
            participant = ChatParticipant.query.filter_by(
                room_id=message.room_id,
                user_id=user_id
            ).first()

            if message.user_id == user_id or (participant and participant.role in ['admin', 'moderator']):
                db.session.delete(message)
                db.session.commit()
                logger.info(f"Message {message_id} deleted by user {user_id}")
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting message: {e}")
            raise
