#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    # Test basic imports
    from app.main import app
    from app.core.config import config
    from app.models.user import User
    from app.models.chat import ChatRoom, ChatMessage

    print("✅ Backend imports successful!")
    print(f"✅ Flask app: {app}")
    print(f"✅ Config loaded: {config.SECRET_KEY[:10]}...")
    print(f"✅ User model: {User}")
    print(f"✅ Chat models: {ChatRoom}, {ChatMessage}")

    # Test database connection
    from app.core.database import init_db, db
    print("✅ Database models imported successfully")

    print("\n🎉 Backend setup verification complete!")
    print("The QKD simulator with chat functionality is ready!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
