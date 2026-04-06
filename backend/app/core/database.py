from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
_is_sqlite = "sqlite" in settings.database_url
_is_memory_sqlite = settings.database_url.endswith(":memory:") or settings.database_url.endswith("/:memory:")

engine_kwargs = {
    "echo": True,  # Set to False in production
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

if _is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}

if _is_memory_sqlite:
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(settings.database_url, **engine_kwargs)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    """Create database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        _run_lightweight_migrations()
        _seed_initial_admin_if_needed()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def _run_lightweight_migrations():
    """Apply lightweight schema upgrades for SQLite development environments."""
    if "sqlite" not in settings.database_url:
        return

    with engine.begin() as conn:
        user_columns = {
            row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()
        }

        if "role" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user' NOT NULL"))

        if "token_version" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN token_version INTEGER DEFAULT 0 NOT NULL"))


def _seed_initial_admin_if_needed():
    if settings.app_env != "development" or not settings.seed_dev_admin:
        return
    try:
        from ..models import User
        from ..services.auth_service import auth_service

        db = SessionLocal()
        has_user = db.query(User.id).first() is not None
        if has_user:
            db.close()
            return

        admin = User(
            username=settings.initial_admin_username,
            email=settings.initial_admin_email,
            hashed_password=auth_service.get_password_hash(settings.initial_admin_password),
            role="admin",
            token_version=0,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.close()
        logger.info("Seeded initial development admin user")
    except Exception as e:
        logger.warning("Initial admin seeding skipped: %s", e)

def get_database_url():
    """Get database URL for Alembic"""
    return settings.database_url
