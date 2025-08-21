#!/usr/bin/env python3
"""
Database setup script for TrackerWorkflow API
This script creates the database tables and optionally adds a test user.
"""

import os
import sys
from sqlalchemy import create_engine
from database import Base, SessionLocal
from models import User
from auth import get_password_hash
from config import settings

def setup_database():
    """Create all database tables"""
    try:
        # Create engine and tables
        engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Check if test user exists
        db = SessionLocal()
        test_user = db.query(User).filter(User.email == "demo@example.com").first()
        
        if not test_user:
            # Create test user
            test_user = User(
                email="demo@example.com",
                password=get_password_hash("password")
            )
            db.add(test_user)
            db.commit()
            print("✅ Test user created: demo@example.com / password")
        else:
            print("ℹ️  Test user already exists: demo@example.com / password")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("Please check your database connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    print("Setting up TrackerWorkflow database...")
    setup_database()
    print("🎉 Database setup complete!") 