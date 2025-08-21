import psycopg2
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_password_column():
    """Fix the password column to allow NULL values"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password
        )
        cursor = conn.cursor()
        
        logger.info("🔗 Connected to database successfully")
        
        # Check current password column constraint
        cursor.execute("""
            SELECT column_name, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'password'
        """)
        
        result = cursor.fetchone()
        if result:
            column_name, is_nullable, column_default = result
            logger.info(f"📋 Current password column: {column_name}, Nullable: {is_nullable}, Default: {column_default}")
            
            if is_nullable == 'NO':
                logger.info("🔧 Fixing password column to allow NULL values...")
                
                # Alter the password column to allow NULL
                cursor.execute("ALTER TABLE users ALTER COLUMN password DROP NOT NULL")
                conn.commit()
                
                logger.info("✅ Password column now allows NULL values")
                
                # Verify the change
                cursor.execute("""
                    SELECT column_name, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'password'
                """)
                
                result = cursor.fetchone()
                if result:
                    column_name, is_nullable, column_default = result
                    logger.info(f"📋 Updated password column: {column_name}, Nullable: {is_nullable}, Default: {column_default}")
            else:
                logger.info("✅ Password column already allows NULL values")
        else:
            logger.error("❌ Password column not found in users table")
            
    except Exception as e:
        logger.error(f"❌ Error fixing password column: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            logger.info("🔌 Database connection closed")

if __name__ == "__main__":
    fix_password_column()
