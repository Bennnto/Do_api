#!/usr/bin/env python3
"""Create a test user for testing registration/login"""

from main import SessionLocal, UserDB, hash_password

def create_test_user():
    db = SessionLocal()
    
    # Check if test user already exists
    existing = db.query(UserDB).filter(UserDB.username == "testuser").first()
    if existing:
        print("✅ Test user already exists!")
        print(f"   Username: testuser")
        print(f"   Email: {existing.email}")
        print(f"   Password: testpass123")
        db.close()
        return
    
    # Create new test user
    test_user = UserDB(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpass123")
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print("✅ Test user created successfully!")
    print(f"   Username: testuser")
    print(f"   Email: test@example.com")
    print(f"   Password: testpass123")
    print(f"   User ID: {test_user.user_id}")
    
    db.close()

if __name__ == "__main__":
    create_test_user()
