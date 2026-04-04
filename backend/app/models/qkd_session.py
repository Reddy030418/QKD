from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class QKDSession(Base):
    """QKD Session model"""
    __tablename__ = "qkd_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # QKD Parameters
    key_length = Column(Integer, nullable=False)
    noise_level = Column(Float, nullable=False)
    detector_efficiency = Column(Float, nullable=False)
    eavesdropper_present = Column(Boolean, default=False)

    # Results
    alice_bits = Column(JSON, nullable=True)  # Alice's random bits
    alice_bases = Column(JSON, nullable=True)  # Alice's polarization bases
    bob_bases = Column(JSON, nullable=True)    # Bob's measurement bases
    bob_measurements = Column(JSON, nullable=True)  # Bob's measurement results
    sifted_key_alice = Column(JSON, nullable=True)  # Alice's sifted key
    sifted_key_bob = Column(JSON, nullable=True)    # Bob's sifted key
    final_shared_key = Column(JSON, nullable=True)  # Final shared key

    # Statistics
    transmitted_photons = Column(Integer, default=0)
    detected_photons = Column(Integer, default=0)
    quantum_error_rate = Column(Float, default=0.0)
    final_key_length = Column(Integer, default=0)

    # Status
    status = Column(String, default="initialized")  # initialized, running, completed, error
    security_status = Column(String, default="unknown")  # secure, compromised, unknown

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="qkd_sessions")

class QKDSessionLog(Base):
    """QKD Session log entries"""
    __tablename__ = "qkd_session_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("qkd_sessions.session_id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(String, default="INFO")  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)  # Additional data for the log entry

    session = relationship("QKDSession", back_populates="logs")

# Add relationship to User model
def setup_relationships():
    """Set up relationships between models after all models are imported"""
    from .user import User
    User.qkd_sessions = relationship("QKDSession", back_populates="user")

QKDSession.logs = relationship("QKDSessionLog", back_populates="session")
