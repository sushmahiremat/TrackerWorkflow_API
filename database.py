from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import os

# Try to get database URL from environment or use fallback
def get_database_url():
    """Get database URL with fallback options"""
    # First try environment variable
    if os.getenv('DATABASE_URL'):
        return os.getenv('DATABASE_URL')
    
    # Fallback to individual settings
    host = os.getenv('DB_HOST', settings.db_host)
    port = os.getenv('DB_PORT', settings.db_port)
    database = os.getenv('DB_NAME', settings.db_name)
    user = os.getenv('DB_USER', settings.db_user)
    password = os.getenv('DB_PASSWORD', settings.db_password)
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

# Create database engine
database_url = get_database_url()
print(f"🔗 Connecting to database: {database_url}")

# Create engine with connection pooling and retry logic
engine = create_engine(
    database_url,
    echo=False,  # Set to False for better performance
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,  # Recycle connections after 5 minutes
    # Performance optimizations
    pool_size=10,  # Reduced for App Runner (was 20)
    max_overflow=20,  # Reduced for App Runner (was 30)
    pool_timeout=30,  # Timeout for connection acquisition
    # Connection optimizations
    connect_args={
        "connect_timeout": 10,  # Connection timeout
        "application_name": "TrackerWorkflow"  # Better monitoring
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 