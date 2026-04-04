-- Quantum Key Distribution Database Initialization Script

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create QKD sessions table
CREATE TABLE qkd_sessions (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL UNIQUE,
    user_id INTEGER,
    key_length INTEGER NOT NULL,
    noise_level REAL NOT NULL,
    detector_efficiency REAL NOT NULL,
    eavesdropper_present INTEGER DEFAULT 0,
    alice_bits TEXT,
    alice_bases TEXT,
    bob_bases TEXT,
    bob_measurements TEXT,
    sifted_key_alice TEXT,
    sifted_key_bob TEXT,
    final_shared_key TEXT,
    transmitted_photons INTEGER DEFAULT 0,
    detected_photons INTEGER DEFAULT 0,
    quantum_error_rate REAL DEFAULT 0.0,
    final_key_length INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'initialized',
    security_status VARCHAR(20) DEFAULT 'unknown',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

-- Create QKD session logs table
CREATE TABLE qkd_session_logs (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10) DEFAULT 'INFO',
    message TEXT NOT NULL,
    data TEXT
);

-- Create indexes for better performance
CREATE INDEX idx_qkd_sessions_user_id ON qkd_sessions(user_id);
CREATE INDEX idx_qkd_sessions_session_id ON qkd_sessions(session_id);
CREATE INDEX idx_qkd_sessions_status ON qkd_sessions(status);
CREATE INDEX idx_qkd_sessions_created_at ON qkd_sessions(created_at);
CREATE INDEX idx_qkd_session_logs_session_id ON qkd_session_logs(session_id);
CREATE INDEX idx_qkd_session_logs_timestamp ON qkd_session_logs(timestamp);
