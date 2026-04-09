from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base

class ChatRoom(Base):
    """Chat room model for organizing conversations"""
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    room_type = Column(String(20), default='general')  # 'general', 'qkd_session', 'private'
    session_id = Column(Integer, ForeignKey('qkd_sessions.id'), nullable=True)  # Link to QKD session if applicable
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="created_rooms")
    session = relationship("QKDSession", back_populates="chat_room")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default='text')  # 'text', 'system', 'ai_response'
    message_metadata = Column(JSON, nullable=True)  # For storing additional message data
    room_id = Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="messages")

class ChatParticipant(Base):
    """Chat room participant model"""
    __tablename__ = "chat_participants"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(20), default='member')  # 'admin', 'moderator', 'member'
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("ChatRoom")
    user = relationship("User")

class AIAgent(Base):
    """AI assistant configuration model"""
    __tablename__ = "ai_agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    model_type = Column(String(50), default='gpt-3.5-turbo')  # AI model identifier
    api_endpoint = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True)  # Encrypted API key
    system_prompt = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="ai_agents")
    conversations = relationship("AIConversation", back_populates="agent", cascade="all, delete-orphan")

class AIConversation(Base):
    """AI conversation history model"""
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('ai_agents.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('chat_rooms.id'), nullable=True)
    title = Column(String(255), nullable=True)
    context = Column(JSON, nullable=True)  # Store conversation context
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent = relationship("AIAgent", back_populates="conversations")
    user = relationship("User")
    room = relationship("ChatRoom")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")

class AIMessage(Base):
    """AI conversation message model"""
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('ai_conversations.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    model_response = Column(JSON, nullable=True)  # Store full AI response metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")
