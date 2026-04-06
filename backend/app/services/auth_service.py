from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.config import settings
from ..models import User

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")


class AuthService:
    """Authentication service for user management"""

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash password with bcrypt, fallback to pbkdf2_sha256 if bcrypt backend is unavailable."""
        try:
            return pwd_context.hash(password, scheme="bcrypt")
        except Exception:
            return pbkdf2_sha256.hash(password)

    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None):
        """Create a short-lived JWT access token."""
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        payload = {
            "sub": user.username,
            "uid": user.id,
            "role": user.role,
            "tv": user.token_version,
            "type": "access",
            "exp": expire,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def create_refresh_token(self, user: User, expires_delta: Optional[timedelta] = None):
        """Create a longer-lived JWT refresh token."""
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
        payload = {
            "sub": user.username,
            "uid": user.id,
            "role": user.role,
            "tv": user.token_version,
            "type": "refresh",
            "exp": expire,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode token payload safely."""
        try:
            return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        except JWTError:
            return None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from valid access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = auth_service.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("uid")
    token_version = payload.get("tv")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if token_version != user.token_version:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)):
    """Ensure current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_roles(*roles: str):
    """Reusable RBAC dependency for admin/user route guards."""
    allowed = {role.strip().lower() for role in roles if role and role.strip()}

    def _role_guard(current_user: User = Depends(get_current_active_user)):
        user_role = (current_user.role or "").lower()
        if allowed and user_role not in allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Access requires one of roles: {', '.join(sorted(allowed))}",
            )
        return current_user

    return _role_guard


# Global auth service instance
auth_service = AuthService()
