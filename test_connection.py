#!/usr/bin/env python3
"""
Simple script to test database connection before running migration.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    try:
        # Try to get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            print(f"🔗 Testing connection with DATABASE_URL: {database_url}")
            conn = psycopg2.connect(database_url)
        else:
            # Fallback to individual settings
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '5432')
            database = os.getenv('DB_NAME', 'TrackerWorkflow')
            user = os.getenv('DB_USER', 'postgres')
            password = os.getenv('DB_PASSWORD', '123')
            
            print(f"🔗 Testing connection with individual settings:")
            print(f"   Host: {host}")
            print(f"   Port: {port}")
            print(f"   Database: {database}")
            print(f"   User: {user}")
            print(f"   Password: {'*' * len(password) if password else 'None'}")
            
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
        
        # Test basic operations
        cursor = conn.cursor()
        
        # Test simple query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Connected successfully!")
        print(f"📊 PostgreSQL version: {version[0]}")
        
        # Test if we can create tables
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()
        print(f"📁 Current database: {db_name[0]}")
        
        # List existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        if tables:
            print(f"📋 Existing tables: {[table[0] for table in tables]}")
        else:
            print("📋 No tables found in database")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your database credentials")
        print("3. Verify database name exists")
        print("4. Check if user has proper permissions")
        return False

if __name__ == "__main__":
    print("🧪 Testing database connection...")
    print("=" * 50)
    
    success = test_connection()
    
    if success:
        print("\n✅ Ready to run migration!")
        print("Run: python update_database.py")
    else:
        print("\n❌ Fix connection issues first!")
