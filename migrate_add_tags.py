"""
Migration script to add 'tags' column to existing tasks table.
Run this script once to update your database schema.

Usage:
    python migrate_add_tags.py
"""
import sys
from sqlalchemy import text
from database import engine, SessionLocal

def migrate():
    """Add tags column to tasks table if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='tasks' AND column_name='tags'
        """))
        
        if result.fetchone():
            print("✅ 'tags' column already exists in tasks table")
            return
        
        # Add the tags column
        print("🔄 Adding 'tags' column to tasks table...")
        db.execute(text("""
            ALTER TABLE tasks 
            ADD COLUMN tags JSON DEFAULT '[]'::json
        """))
        db.commit()
        print("✅ Successfully added 'tags' column to tasks table")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        print("\n💡 If you're using SQLite, you may need to recreate the database.")
        print("   For PostgreSQL, make sure you have proper permissions.")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting migration to add tags column...")
    migrate()
    print("✨ Migration completed!")

