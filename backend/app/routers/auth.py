from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import logging
from ..core.database import get_db
from ..core.config import settings
from ..models import User
from ..services.auth_service import AuthService, get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)
auth_service = AuthService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

from fastapi import Body

@router.post("/register")
async def register_user(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )

        # Create new user
        hashed_password = auth_service.get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User {username} registered successfully")

        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "username": new_user.username
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/test-login")
async def test_login(
    username: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Test login - simplified for demo purposes"""
    try:
        # Hardcoded test credentials for demo
        test_creds = {
            "alice": "alice123",
            "bob": "bob123",
            "eve": "eve123",
            "testuser": "testpass"
        }
        
        if username not in test_creds:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if password != test_creds[username]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        logger.info(f"Test login successful for {username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": 1,
            "username": username
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in test login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    try:
        # Find user by username
        user = db.query(User).filter(User.username == form_data.username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        is_valid = auth_service.verify_password(form_data.password, user.hashed_password)
        logger.info(f"Password verification for {form_data.username}: {is_valid}")
        logger.info(f"Stored hash: {user.hashed_password[:50]}...")
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Generate access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        logger.info(f"User {user.username} logged in successfully")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me")
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active
    }

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}
