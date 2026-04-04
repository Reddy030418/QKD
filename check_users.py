import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal, engine, Base
from app.models import User

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    users = db.query(User).all()
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"\nUsername: {user.username}")
        print(f"Hash format: {user.hashed_password[:20]}...")
        print(f"Full hash: {user.hashed_password}")
finally:
    db.close()
