from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .core.database import db, get_db
from .models.user import User
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'error': 'Username, email, and password are required'}), 400

        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return jsonify({'error': 'Username or email already registered'}), 400

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        logger.info(f"User {username} registered successfully")

        return jsonify({
            "message": "User registered successfully",
            "user_id": new_user.id,
            "username": new_user.username
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering user: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({'error': 'Username and password are required'}), 400

        # Find user by username
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.hashed_password, password):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'User account is inactive'}), 400

        # Generate access token
        access_token = create_access_token(identity=user.username)

        logger.info(f"User {user.username} logged in successfully")

        return jsonify({
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        }), 200

    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active
        }), 200

    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({"message": "Successfully logged out"}), 200
