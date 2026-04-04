import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal, engine, Base
from app.models import User
from app.services.auth_service import AuthService

# Initialize
Base.metadata.create_all(bind=engine)
auth_service = AuthService()
db = SessionLocal()

try:
    # Get alice user
    user = db.query(User).filter(User.username == 'alice').first()
    if not user:
        print('User alice not found')
    else:
        print(f'User found: {user.username}')
        print(f'Stored hash: {user.hashed_password}')
        
        # Test verification
        password = 'alice123'
        is_valid = auth_service.verify_password(password, user.hashed_password)
        print(f'Password verification: {is_valid}')
        
        # Debug the hash
        parts = user.hashed_password.split('$')
        print(f'Hash parts count: {len(parts)}')
        if len(parts) >= 3:
            print(f'  Algorithm: {parts[0]}')
            print(f'  Salt: {parts[1]}')
            print(f'  Hash: {parts[2][:50]}...')
finally:
    db.close()
