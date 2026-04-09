from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services.chat_service import ChatService
from .services.ai_service import AIService
from .models import ChatRoom, ChatMessage, ChatParticipant, AIConversation
import logging

logger = logging.getLogger(__name__)

# Create chat blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Chat Room endpoints
@chat_bp.route('/rooms', methods=['GET'])
@jwt_required()
def get_user_rooms():
    """Get all chat rooms for the current user"""
    try:
        user_id = get_jwt_identity()
        rooms_data = ChatService.get_user_rooms_with_unread(user_id)

        result = []
        for room_data in rooms_data:
            room = room_data['room']
            result.append({
                'id': room.id,
                'name': room.name,
                'description': room.description,
                'room_type': room.room_type,
                'session_id': room.session_id,
                'created_by': room.created_by,
                'created_at': room.created_at.isoformat(),
                'message_count': room_data['message_count'],
                'last_message': {
                    'content': room_data['last_message'].content,
                    'created_at': room_data['last_message'].created_at.isoformat(),
                    'user_id': room_data['last_message'].user_id
                } if room_data['last_message'] else None
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting user rooms: {e}")
        return jsonify({'error': 'Failed to get chat rooms'}), 500

@chat_bp.route('/rooms', methods=['POST'])
@jwt_required()
def create_room():
    """Create a new chat room"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('name'):
            return jsonify({'error': 'Room name is required'}), 400

        room = ChatService.create_room(
            name=data['name'],
            description=data.get('description', ''),
            created_by=user_id,
            room_type=data.get('room_type', 'general'),
            session_id=data.get('session_id')
        )

        return jsonify({
            'id': room.id,
            'name': room.name,
            'description': room.description,
            'room_type': room.room_type,
            'session_id': room.session_id,
            'created_by': room.created_by,
            'created_at': room.created_at.isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        return jsonify({'error': 'Failed to create chat room'}), 500

@chat_bp.route('/rooms/<int:room_id>', methods=['GET'])
@jwt_required()
def get_room(room_id):
    """Get a specific chat room"""
    try:
        user_id = get_jwt_identity()
        room = ChatService.get_room(room_id)

        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Check if user is a participant
        participant = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
        if not participant:
            return jsonify({'error': 'Access denied'}), 403

        return jsonify({
            'id': room.id,
            'name': room.name,
            'description': room.description,
            'room_type': room.room_type,
            'session_id': room.session_id,
            'created_by': room.created_by,
            'created_at': room.created_at.isoformat(),
            'updated_at': room.updated_at.isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting room: {e}")
        return jsonify({'error': 'Failed to get chat room'}), 500

@chat_bp.route('/rooms/<int:room_id>/messages', methods=['GET'])
@jwt_required()
def get_room_messages(room_id):
    """Get messages from a chat room"""
    try:
        user_id = get_jwt_identity()
        room = ChatService.get_room(room_id)

        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Check if user is a participant
        participant = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
        if not participant:
            return jsonify({'error': 'Access denied'}), 403

        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        messages = ChatService.get_room_messages(room_id, limit, offset)
        result = []

        for message in messages:
            result.append({
                'id': message.id,
                'content': message.content,
                'message_type': message.message_type,
                'metadata': message.metadata,
                'user_id': message.user_id,
                'created_at': message.created_at.isoformat(),
                'updated_at': message.updated_at.isoformat()
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting room messages: {e}")
        return jsonify({'error': 'Failed to get messages'}), 500

@chat_bp.route('/rooms/<int:room_id>/messages', methods=['POST'])
@jwt_required()
def send_message(room_id):
    """Send a message to a chat room"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('content'):
            return jsonify({'error': 'Message content is required'}), 400

        room = ChatService.get_room(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Check if user is a participant
        participant = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
        if not participant:
            return jsonify({'error': 'Access denied'}), 403

        message = ChatService.send_message(
            room_id=room_id,
            user_id=user_id,
            content=data['content'],
            message_type=data.get('message_type', 'text'),
            metadata=data.get('metadata')
        )

        return jsonify({
            'id': message.id,
            'content': message.content,
            'message_type': message.message_type,
            'metadata': message.metadata,
            'user_id': message.user_id,
            'created_at': message.created_at.isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({'error': 'Failed to send message'}), 500

@chat_bp.route('/rooms/<int:room_id>/participants', methods=['GET'])
@jwt_required()
def get_room_participants(room_id):
    """Get all participants in a chat room"""
    try:
        user_id = get_jwt_identity()
        room = ChatService.get_room(room_id)

        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Check if user is a participant
        participant = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
        if not participant:
            return jsonify({'error': 'Access denied'}), 403

        participants = ChatService.get_room_participants(room_id)
        result = []

        for p in participants:
            result.append({
                'id': p.id,
                'user_id': p.user_id,
                'role': p.role,
                'joined_at': p.joined_at.isoformat(),
                'last_seen_at': p.last_seen_at.isoformat()
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting room participants: {e}")
        return jsonify({'error': 'Failed to get participants'}), 500

@chat_bp.route('/rooms/<int:room_id>/participants', methods=['POST'])
@jwt_required()
def add_participant(room_id):
    """Add a participant to a chat room"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('user_id'):
            return jsonify({'error': 'User ID is required'}), 400

        room = ChatService.get_room(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Check if current user is admin or moderator
        current_participant = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
        if not current_participant or current_participant.role not in ['admin', 'moderator']:
            return jsonify({'error': 'Insufficient permissions'}), 403

        participant = ChatService.add_participant(
            room_id=room_id,
            user_id=data['user_id'],
            role=data.get('role', 'member')
        )

        return jsonify({
            'id': participant.id,
            'user_id': participant.user_id,
            'role': participant.role,
            'joined_at': participant.joined_at.isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error adding participant: {e}")
        return jsonify({'error': 'Failed to add participant'}), 500

@chat_bp.route('/messages/search', methods=['GET'])
@jwt_required()
def search_messages():
    """Search messages in a room"""
    try:
        user_id = get_jwt_identity()
        room_id = request.args.get('room_id', type=int)
        query = request.args.get('q', '')

        if not room_id or not query:
            return jsonify({'error': 'Room ID and query are required'}), 400

        room = ChatService.get_room(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Check if user is a participant
        participant = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
        if not participant:
            return jsonify({'error': 'Access denied'}), 403

        messages = ChatService.search_messages(room_id, query)
        result = []

        for message in messages:
            result.append({
                'id': message.id,
                'content': message.content,
                'message_type': message.message_type,
                'user_id': message.user_id,
                'created_at': message.created_at.isoformat()
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return jsonify({'error': 'Failed to search messages'}), 500

# AI Assistant endpoints
@chat_bp.route('/ai/agents', methods=['GET'])
@jwt_required()
def get_ai_agents():
    """Get all AI agents for the current user"""
    try:
        user_id = get_jwt_identity()
        agents = AIService.get_user_agents(user_id)

        result = []
        for agent in agents:
            result.append({
                'id': agent.id,
                'name': agent.name,
                'description': agent.description,
                'model_type': agent.model_type,
                'is_active': bool(agent.is_active),
                'created_at': agent.created_at.isoformat(),
                'updated_at': agent.updated_at.isoformat()
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting AI agents: {e}")
        return jsonify({'error': 'Failed to get AI agents'}), 500

@chat_bp.route('/ai/agents', methods=['POST'])
@jwt_required()
def create_ai_agent():
    """Create a new AI agent"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('name'):
            return jsonify({'error': 'Agent name is required'}), 400

        agent = AIService.create_agent(
            name=data['name'],
            description=data.get('description', ''),
            model_type=data.get('model_type', 'gpt-3.5-turbo'),
            api_endpoint=data.get('api_endpoint'),
            api_key=data.get('api_key'),
            system_prompt=data.get('system_prompt'),
            created_by=user_id
        )

        return jsonify({
            'id': agent.id,
            'name': agent.name,
            'description': agent.description,
            'model_type': agent.model_type,
            'is_active': bool(agent.is_active),
            'created_at': agent.created_at.isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error creating AI agent: {e}")
        return jsonify({'error': 'Failed to create AI agent'}), 500

@chat_bp.route('/ai/conversations', methods=['GET'])
@jwt_required()
def get_ai_conversations():
    """Get all AI conversations for the current user"""
    try:
        user_id = get_jwt_identity()
        conversations = AIService.get_user_conversations(user_id)

        result = []
        for conv in conversations:
            result.append({
                'id': conv.id,
                'agent_id': conv.agent_id,
                'title': conv.title,
                'context': conv.context,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting AI conversations: {e}")
        return jsonify({'error': 'Failed to get AI conversations'}), 500

@chat_bp.route('/ai/conversations', methods=['POST'])
@jwt_required()
def create_ai_conversation():
    """Create a new AI conversation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('agent_id'):
            return jsonify({'error': 'Agent ID is required'}), 400

        conversation = AIService.create_conversation(
            agent_id=data['agent_id'],
            user_id=user_id,
            title=data.get('title'),
            context=data.get('context')
        )

        return jsonify({
            'id': conversation.id,
            'agent_id': conversation.agent_id,
            'title': conversation.title,
            'context': conversation.context,
            'created_at': conversation.created_at.isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error creating AI conversation: {e}")
        return jsonify({'error': 'Failed to create AI conversation'}), 500

@chat_bp.route('/ai/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_ai_conversation_messages(conversation_id):
    """Get messages from an AI conversation"""
    try:
        user_id = get_jwt_identity()
        conversation = AIConversation.query.filter_by(id=conversation_id, user_id=user_id).first()

        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        messages = AIService.get_conversation_messages(conversation_id)
        result = []

        for message in messages:
            result.append({
                'id': message.id,
                'role': message.role,
                'content': message.content,
                'tokens_used': message.tokens_used,
                'created_at': message.created_at.isoformat()
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting AI conversation messages: {e}")
        return jsonify({'error': 'Failed to get AI conversation messages'}), 500

@chat_bp.route('/ai/conversations/<int:conversation_id>/messages', methods=['POST'])
@jwt_required()
def send_ai_message(conversation_id):
    """Send a message to an AI conversation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('content'):
            return jsonify({'error': 'Message content is required'}), 400

        conversation = AIConversation.query.filter_by(id=conversation_id, user_id=user_id).first()
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        # Add user message
        user_message = AIService.add_message(
            conversation_id=conversation_id,
            role='user',
            content=data['content']
        )

        # Get conversation context for AI
        messages = AIService.get_conversation_messages(conversation_id)
        context = []

        for msg in messages[:-1]:  # Exclude the current user message
            context.append({
                'role': msg.role,
                'content': msg.content
            })

        # Send to AI agent
        ai_response_data = AIService.send_to_ai_agent(
            conversation.agent_id,
            data['content'],
            context
        )

        # Add AI response
        ai_message = AIService.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=ai_response_data['response'],
            tokens_used=ai_response_data['tokens_used'],
            model_response=ai_response_data['model_response']
        )

        # Update agent activity
        AIService.update_agent_activity(conversation.agent_id)

        return jsonify({
            'user_message': {
                'id': user_message.id,
                'role': user_message.role,
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'ai_message': {
                'id': ai_message.id,
                'role': ai_message.role,
                'content': ai_message.content,
                'tokens_used': ai_message.tokens_used,
                'created_at': ai_message.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        logger.error(f"Error sending AI message: {e}")
        return jsonify({'error': 'Failed to send AI message'}), 500
