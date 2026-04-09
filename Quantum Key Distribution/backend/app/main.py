from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .core.database import init_db, db
from .core.config import config
from .auth import auth_bp
from .qkd import qkd_bp
from .sessions import sessions_bp
from .chat import chat_bp
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

# Initialize extensions
CORS(app, origins=config.CORS_ORIGINS)
jwt = JWTManager(app)

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(qkd_bp, url_prefix='/qkd')
app.register_blueprint(sessions_bp, url_prefix='/sessions')
app.register_blueprint(chat_bp)



# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "QKD Backend API with Chat",
        "version": "1.0.0"
    })

# Root endpoint
@app.route('/')
def root():
    return jsonify({
        "message": "Quantum Key Distribution (BB84) API with Chat",
        "docs": "/docs",
        "health": "/health",
        "chat": "WebSocket chat available at /socket.io",
        "api": {
            "auth": "/auth/*",
            "qkd": "/qkd/*",
            "sessions": "/sessions/*",
            "chat": "/api/chat/*"
        }
    })

if __name__ == '__main__':
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
