from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
import secrets
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.config import settings
from ..models import User

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class AuthService:
    """Authentication service for user management"""

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash"""
        try:
            logger.info(f"DEBUG: verify_password called with hash prefix: {hashed_password[:30]}...")
            # Expect format: algorithm$salt$hash
            parts = hashed_password.split('$')
            logger.info(f"DEBUG: Hash parts: {len(parts)}, algo: {parts[0] if parts else 'N/A'}")
            
            if len(parts) != 3 or parts[0] != 'sha256':
                logger.warning(f"DEBUG: Invalid hash format")
                return False
            salt = parts[1]
            stored_hash = parts[2]
            # Recreate hash with stored salt
            new_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
            result = (new_hash == stored_hash)
            logger.info(f"DEBUG: Password verify result: {result}, computed_hash[:20]={new_hash[:20]}, stored_hash[:20]={stored_hash[:20]}")
            return result
        except Exception as e:
            logger.error(f"DEBUG: Exception in verify_password: {e}", exc_info=True)
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash a password with salt"""
        # Generate random salt
        salt = secrets.token_hex(16)
        # Create hash with salt
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        # Return in format: algorithm$salt$hash
        return f"sha256${salt}${password_hash}"

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return the username"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = auth_service.verify_token(token)
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Global auth service instance
auth_service = AuthService()
