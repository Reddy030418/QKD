from ..core.database import db
from datetime import datetime
import json

class QKDSession(db.Model):
    """QKD Session model"""
    __tablename__ = "qkd_sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # QKD Parameters
    key_length = db.Column(db.Integer, nullable=False)
    noise_level = db.Column(db.Float, nullable=False)
    detector_efficiency = db.Column(db.Float, nullable=False)
    eavesdropper_present = db.Column(db.Boolean, default=False)

    # Results (stored as JSON strings)
    alice_bits = db.Column(db.Text, nullable=True)  # Alice's random bits
    alice_bases = db.Column(db.Text, nullable=True)  # Alice's polarization bases
    bob_bases = db.Column(db.Text, nullable=True)    # Bob's measurement bases
    bob_measurements = db.Column(db.Text, nullable=True)  # Bob's measurement results
    sifted_key_alice = db.Column(db.Text, nullable=True)  # Alice's sifted key
    sifted_key_bob = db.Column(db.Text, nullable=True)    # Bob's sifted key
    final_shared_key = db.Column(db.Text, nullable=True)  # Final shared key

    # Statistics
    transmitted_photons = db.Column(db.Integer, default=0)
    detected_photons = db.Column(db.Integer, default=0)
    quantum_error_rate = db.Column(db.Float, default=0.0)
    final_key_length = db.Column(db.Integer, default=0)

    # Status
    status = db.Column(db.String(50), default="initialized")  # initialized, running, completed, error
    security_status = db.Column(db.String(50), default="unknown")  # secure, compromised, unknown

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationship with logs
    logs = db.relationship('QKDSessionLog', backref='session', lazy=True, cascade='all, delete-orphan')

    # Relationship with chat room
    chat_room = db.relationship('ChatRoom', back_populates='session', uselist=False)

    @property
    def alice_bits_list(self):
        """Get alice_bits as list"""
        return json.loads(self.alice_bits) if self.alice_bits else []

    @alice_bits_list.setter
    def alice_bits_list(self, value):
        """Set alice_bits from list"""
        self.alice_bits = json.dumps(value) if value else None

    @property
    def alice_bases_list(self):
        """Get alice_bases as list"""
        return json.loads(self.alice_bases) if self.alice_bases else []

    @alice_bases_list.setter
    def alice_bases_list(self, value):
        """Set alice_bases from list"""
        self.alice_bases = json.dumps(value) if value else None

    @property
    def bob_bases_list(self):
        """Get bob_bases as list"""
        return json.loads(self.bob_bases) if self.bob_bases else []

    @bob_bases_list.setter
    def bob_bases_list(self, value):
        """Set bob_bases from list"""
        self.bob_bases = json.dumps(value) if value else None

    @property
    def bob_measurements_list(self):
        """Get bob_measurements as list"""
        return json.loads(self.bob_measurements) if self.bob_measurements else []

    @bob_measurements_list.setter
    def bob_measurements_list(self, value):
        """Set bob_measurements from list"""
        self.bob_measurements = json.dumps(value) if value else None

    @property
    def sifted_key_alice_list(self):
        """Get sifted_key_alice as list"""
        return json.loads(self.sifted_key_alice) if self.sifted_key_alice else []

    @sifted_key_alice_list.setter
    def sifted_key_alice_list(self, value):
        """Set sifted_key_alice from list"""
        self.sifted_key_alice = json.dumps(value) if value else None

    @property
    def sifted_key_bob_list(self):
        """Get sifted_key_bob as list"""
        return json.loads(self.sifted_key_bob) if self.sifted_key_bob else []

    @sifted_key_bob_list.setter
    def sifted_key_bob_list(self, value):
        """Set sifted_key_bob from list"""
        self.sifted_key_bob = json.dumps(value) if value else None

    @property
    def final_shared_key_list(self):
        """Get final_shared_key as list"""
        return json.loads(self.final_shared_key) if self.final_shared_key else []

    @final_shared_key_list.setter
    def final_shared_key_list(self, value):
        """Set final_shared_key from list"""
        self.final_shared_key = json.dumps(value) if value else None

class QKDSessionLog(db.Model):
    """QKD Session log entries"""
    __tablename__ = "qkd_session_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(255), db.ForeignKey('qkd_sessions.session_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20), default="INFO")  # INFO, WARNING, ERROR, DEBUG
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=True)  # Additional data for the log entry (JSON string)

    @property
    def data_dict(self):
        """Get data as dictionary"""
        return json.loads(self.data) if self.data else {}

    @data_dict.setter
    def data_dict(self, value):
        """Set data from dictionary"""
        self.data = json.dumps(value) if value else None
