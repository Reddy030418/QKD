from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
import logging
from ..core.database import get_db
from ..core.config import settings
from ..core.rate_limit import auth_rate_limit
from ..core.audit import log_audit_event
from ..models import User
from ..services.auth_service import get_current_active_user, require_roles, auth_service

router = APIRouter()
logger = logging.getLogger(__name__)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    class Config:
        extra = "forbid"

    @validator("username")
    def validate_username(cls, value: str) -> str:
        candidate = value.strip()
        if not candidate.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, '-' and '_'")
        return candidate

    @validator("email")
    def validate_email(cls, value: str) -> str:
        candidate = value.strip().lower()
        if "@" not in candidate or "." not in candidate.split("@")[-1]:
            raise ValueError("Invalid email format")
        return candidate

    @validator("password")
    def validate_password_strength(cls, value: str) -> str:
        if not any(ch.isupper() for ch in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(ch.islower() for ch in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("Password must contain at least one digit")
        return value


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=128)

    class Config:
        extra = "forbid"

    @validator("username")
    def normalize_username(cls, value: str) -> str:
        return value.strip()


class RefreshRequest(BaseModel):
    refresh_token: str

    class Config:
        extra = "forbid"


@router.post("/register")
async def register_user(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    auth_rate_limit(request)
    try:
        existing_user = db.query(User).filter(
            (User.username == payload.username) | (User.email == payload.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )

        role = "admin" if db.query(User).count() == 0 else "user"

        new_user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=auth_service.get_password_hash(payload.password),
            role=role,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info("User %s registered successfully", payload.username)
        log_audit_event("auth.register", actor=new_user, outcome="success")

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role,
            },
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error registering user")
        log_audit_event("auth.register", outcome="failure", reason="internal_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access + refresh tokens."""
    auth_rate_limit(request)
    try:
        user = db.query(User).filter(User.username == payload.username).first()

        if not user or not auth_service.verify_password(payload.password, user.hashed_password):
            log_audit_event(
                "auth.login",
                actor=user,
                outcome="failure",
                reason="invalid_credentials",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            log_audit_event("auth.login", actor=user, outcome="failure", reason="inactive_user")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

        access_token = auth_service.create_access_token(
            user=user,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        refresh_token = auth_service.create_refresh_token(user=user)

        logger.info("User %s logged in successfully", user.username)
        log_audit_event("auth.login", actor=user, outcome="success")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error during login")
        log_audit_event("auth.login", outcome="failure", reason="internal_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/refresh")
async def refresh_token(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    """Exchange refresh token for a new access token."""
    auth_rate_limit(request)
    decoded = auth_service.decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        log_audit_event("auth.refresh", outcome="failure", reason="invalid_refresh_token")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == decoded.get("uid")).first()
    if not user:
        log_audit_event("auth.refresh", outcome="failure", reason="invalid_refresh_token")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if user.token_version != decoded.get("tv"):
        log_audit_event("auth.refresh", actor=user, outcome="failure", reason="token_expired")
        raise HTTPException(status_code=401, detail="Refresh token expired")

    access_token = auth_service.create_access_token(
        user=user,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me")
async def get_current_user(current_user: User = Depends(require_roles("admin", "user"))):
    """Get current user information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Invalidate current access/refresh token family for user."""
    current_user.token_version += 1
    db.add(current_user)
    db.commit()
    log_audit_event("auth.logout", actor=current_user, outcome="success")

    return {"message": "Successfully logged out"}
