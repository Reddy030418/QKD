#!/usr/bin/env python
"""Create test users for QKD application"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal, Base, engine
from app.models import User
from app.services.auth_service import AuthService
from datetime import datetime

def main():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize auth service
    auth_service = AuthService()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test users to create
        test_users = [
            ('alice', 'alice@example.com', 'password123'),
            ('bob', 'bob@example.com', 'password123'),
            ('eve', 'eve@example.com', 'password123'),
            ('testuser', 'test@example.com', 'testpass'),
        ]
        
        created_count = 0
        for username, email, password in test_users:
            # Check if user exists
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                print(f'✓ User {username} already exists')
                continue
            
            # Create new user
            try:
                hashed_password = auth_service.get_password_hash(password)
                new_user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_user)
                print(f'✓ Created user: {username} / {password}')
                created_count += 1
            except Exception as e:
                print(f'✗ Error creating {username}: {e}')
        
        db.commit()
        print(f'\n✓ Successfully created {created_count} test users!')
        print('\nYou can now login with:')
        for username, email, password in test_users:
            print(f'  Username: {username}  Password: {password}')
        
    except Exception as e:
        print(f'✗ Error: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    main()
