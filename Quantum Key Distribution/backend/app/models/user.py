from ..core.database import db
from datetime import datetime

class User(db.Model):
    """User model for authentication"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    hashed_password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with QKD sessions
    qkd_sessions = db.relationship('QKDSession', backref='user', lazy=True)

    # Chat relationships
    created_rooms = db.relationship('ChatRoom', back_populates='creator', lazy=True)
    messages = db.relationship('ChatMessage', back_populates='sender', lazy=True)
    ai_agents = db.relationship('AIAgent', back_populates='creator', lazy=True)
