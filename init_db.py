#!/usr/bin/env python3
"""
Database initialization script for TrackerWorkflow API
"""

import os
import sys
from sqlalchemy import create_engine
from database import Base, SessionLocal
from models import User
from auth import get_password_hash
from config import settings

def init_database():
    """Initialize the database with tables and test data"""
    try:
        print("🔧 Initializing TrackerWorkflow database...")
        
        # Create engine and tables
        engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Create test user
        db = SessionLocal()
        
        # Check if demo user exists
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        
        if not demo_user:
            # Create demo user
            demo_user = User(
                email="demo@example.com",
                password=get_password_hash("password")
            )
            db.add(demo_user)
            db.commit()
            print("✅ Demo user created: demo@example.com / password")
        else:
            print("ℹ️  Demo user already exists: demo@example.com / password")
        
        # Check if test user exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not test_user:
            # Create test user
            test_user = User(
                email="test@example.com",
                password=get_password_hash("testpassword123")
            )
            db.add(test_user)
            db.commit()
            print("✅ Test user created: test@example.com / testpassword123")
        else:
            print("ℹ️  Test user already exists: test@example.com / testpassword123")
        
        db.close()
        print("🎉 Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("Please check your database connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    init_database() 