from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from flask import Flask
from .config import config
import logging

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

# Base class for all models
Base = db.Model

# Create engine/session for direct SQLAlchemy usage in services
engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

def init_db(app: Flask):
    """Initialize database with Flask app"""
    global engine
    app.config.from_object(config)

    # Configure MySQL connection
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = config.SQLALCHEMY_ENGINE_OPTIONS

    db.init_app(app)

    # Import models to register them with SQLAlchemy
    from ..models import User, QKDSession, QKDSessionLog, ChatRoom, ChatMessage, ChatParticipant, AIAgent, AIConversation, AIMessage

    # Create tables
    with app.app_context():
        try:
            engine = db.engine
            SessionLocal.configure(bind=engine)
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

def get_db():
    """Database session dependency"""
    try:
        db_session = db.session
        yield db_session
    finally:
        db_session.close()

def get_database_url():
    """Get database URL for migrations"""
    return config.SQLALCHEMY_DATABASE_URI

