#!/usr/bin/env python3
"""
Database migration script to add Google OAuth columns to existing users table.
Run this script to update your PostgreSQL database schema.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get database connection from environment variables"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Fallback to individual environment variables
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'trackerworkflow_db')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        return psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
    
    # Parse DATABASE_URL
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgres://')
    
    return psycopg2.connect(database_url)

def check_and_create_users_table():
    """Check if users table exists and create it if it doesn't"""
    conn = None
    try:
        conn = get_database_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("🔧 Users table doesn't exist. Creating it...")
            
            # Create users table with all required columns
            create_table_sql = """
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                email VARCHAR UNIQUE NOT NULL,
                password VARCHAR,
                name VARCHAR,
                avatar_url VARCHAR,
                google_id VARCHAR UNIQUE,
                auth_provider VARCHAR DEFAULT 'email',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            cursor.execute(create_table_sql)
            print("✅ Users table created successfully with all required columns!")
            return True
        else:
            print("✅ Users table already exists")
            return False
            
    except Exception as e:
        print(f"❌ Error checking/creating users table: {e}")
        raise
    finally:
        if conn:
            conn.close()

def update_database_schema():
    """Update the database schema to add Google OAuth columns"""
    conn = None
    try:
        conn = get_database_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔍 Checking current database schema...")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('name', 'avatar_url', 'google_id', 'auth_provider', 'is_active')
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns one by one
        columns_to_add = []
        
        if 'name' not in existing_columns:
            columns_to_add.append("name VARCHAR")
        
        if 'avatar_url' not in existing_columns:
            columns_to_add.append("avatar_url VARCHAR")
        
        if 'google_id' not in existing_columns:
            columns_to_add.append("google_id VARCHAR UNIQUE")
        
        if 'auth_provider' not in existing_columns:
            columns_to_add.append("auth_provider VARCHAR DEFAULT 'email'")
        
        if 'is_active' not in existing_columns:
            columns_to_add.append("is_active BOOLEAN DEFAULT TRUE")
        
        if columns_to_add:
            print("🔧 Adding missing columns...")
            
            # Add each column separately to avoid SQL syntax errors
            for column_def in columns_to_add:
                alter_sql = f"ALTER TABLE users ADD COLUMN {column_def}"
                print(f"Executing: {alter_sql}")
                
                try:
                    cursor.execute(alter_sql)
                    print(f"✅ Added column: {column_def}")
                except Exception as column_error:
                    print(f"⚠️ Warning adding column {column_def}: {column_error}")
                    # Continue with other columns
            
            print("✅ Database schema update completed!")
        else:
            print("✅ All required columns already exist!")
        
        # Show final schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Final users table schema:")
        print(f"{'Column Name':<20} {'Data Type':<15} {'Nullable':<10} {'Default':<15}")
        print("-" * 60)
        
        for row in cursor.fetchall():
            column_name, data_type, is_nullable, column_default = row
            default = str(column_default) if column_default else 'NULL'
            print(f"{column_name:<20} {data_type:<15} {is_nullable:<10} {default:<15}")
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def create_sample_user():
    """Create a sample user for testing"""
    conn = None
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Check if demo user exists
        cursor.execute("SELECT id FROM users WHERE email = 'demo@example.com'")
        if cursor.fetchone():
            print("✅ Demo user already exists")
            return
        
        # Create demo user
        cursor.execute("""
            INSERT INTO users (email, password, name, auth_provider, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, ('demo@example.com', 'hashed_password_here', 'Demo User', 'email', True))
        
        conn.commit()
        print("✅ Demo user created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print("=" * 50)
    
    try:
        # First check and create users table if needed
        check_and_create_users_table()
        print("\n" + "=" * 50)
        
        # Then update schema if needed
        update_database_schema()
        print("\n" + "=" * 50)
        
        # Finally create sample user
        create_sample_user()
        print("\n🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"\n💥 Migration failed: {e}")
        print("\nPlease check your database connection and try again.")
