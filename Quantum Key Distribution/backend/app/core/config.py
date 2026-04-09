import os
import tempfile
from typing import List
from dotenv import load_dotenv

load_dotenv()

local_appdata = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
default_data_dir = os.path.join(local_appdata, 'QKDSimulator', 'data')

try:
    os.makedirs(default_data_dir, exist_ok=True)
    default_db_path = os.path.join(default_data_dir, 'qkd.db')
except OSError:
    # Fallback if backend/data is not writable in a specific environment.
    default_db_path = os.path.join(tempfile.gettempdir(), 'qkd_app.db')

default_db_path = default_db_path.replace('\\', '/')
env_db_url = os.environ.get('DATABASE_URL')
normalized_env_db_url = (env_db_url or '').lower().replace('\\', '/')
if env_db_url and 'qkd_app.db' in normalized_env_db_url and '/temp/' in normalized_env_db_url:
    env_db_url = None

class Config:
    """Flask application configuration"""

    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8000))

    # Database Settings
    SQLALCHEMY_DATABASE_URI = env_db_url or f'sqlite:///{default_db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 30))  # minutes

    # QKD Settings
    DEFAULT_KEY_LENGTH = int(os.environ.get('DEFAULT_KEY_LENGTH', 50))
    DEFAULT_NOISE_LEVEL = int(os.environ.get('DEFAULT_NOISE_LEVEL', 5))
    DEFAULT_DETECTOR_EFFICIENCY = int(os.environ.get('DEFAULT_DETECTOR_EFFICIENCY', 95))
    MAX_KEY_LENGTH = int(os.environ.get('MAX_KEY_LENGTH', 500))
    MIN_KEY_LENGTH = int(os.environ.get('MIN_KEY_LENGTH', 10))

    # WebSocket Settings
    WEBSOCKET_PING_INTERVAL = int(os.environ.get('WEBSOCKET_PING_INTERVAL', 20))
    WEBSOCKET_PING_TIMEOUT = int(os.environ.get('WEBSOCKET_PING_TIMEOUT', 20))

    # CORS Settings
    CORS_ORIGINS: List[str] = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')

    # Logging Settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # API Settings
    API_TITLE = "Quantum Key Distribution API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Backend API for BB84 Quantum Key Distribution simulation with Chat functionality"

# Create config instance
config = Config()
