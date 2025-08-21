import time
from sqlalchemy.orm import Session
from models import User, Project, Task
from schemas import UserCreate, ProjectCreate, TaskCreate, GoogleUserInfo
from auth import get_password_hash, verify_password

# Simple in-memory cache for user lookups
_user_cache = {}

def get_cached_user(email_or_google_id: str) -> User:
    """Get user from cache if available"""
    return _user_cache.get(email_or_google_id)

def set_cached_user(user: User):
    """Cache user for future lookups"""
    if user.email:
        _user_cache[user.email] = user
    if user.google_id:
        _user_cache[user.google_id] = user

def clear_user_cache():
    """Clear user cache (useful for testing)"""
    _user_cache.clear()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str):
    return db.query(User).filter(User.google_id == google_id).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, 
        password=hashed_password,
        auth_provider="email"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_or_get_google_user(db: Session, google_user: GoogleUserInfo):
    start_time = time.time()
    print(f"🗄️ CRUD: Starting create_or_get_google_user for {google_user.email}")
    
    try:
        # Check cache first
        cached_user = get_cached_user(google_user.email) or get_cached_user(google_user.sub)
        if cached_user:
            print(f"⚡ CRUD: User found in cache, skipping database query")
            return cached_user
        
        # Optimized: Single query to check both Google ID and email
        step1_start = time.time()
        existing_user = db.query(User).filter(
            (User.google_id == google_user.sub) | (User.email == google_user.email)
        ).first()
        step1_time = time.time() - step1_start
        print(f"🔍 CRUD: Combined lookup completed in {step1_time:.2f}s")
        
        if existing_user:
            # Update existing user if needed
            if not existing_user.google_id:
                existing_user.google_id = google_user.sub
                existing_user.name = google_user.name or existing_user.name
                existing_user.avatar_url = google_user.picture or existing_user.avatar_url
                existing_user.auth_provider = "google"
                db.commit()
                print(f"🔄 CRUD: User updated with Google info")
            
            # Cache the user for future lookups
            set_cached_user(existing_user)
            
            total_time = time.time() - start_time
            print(f"✅ CRUD: Existing user found in {total_time:.2f}s")
            return existing_user
        
        # Create new Google user
        step2_start = time.time()
        db_user = User(
            email=google_user.email,
            google_id=google_user.sub,
            name=google_user.name,
            avatar_url=google_user.picture,
            auth_provider="google"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        step2_time = time.time() - step2_start
        
        # Cache the new user
        set_cached_user(db_user)
        
        total_time = time.time() - start_time
        print(f"🆕 CRUD: New Google user created in {step2_time:.2f}s, total: {total_time:.2f}s")
        return db_user
        
    except Exception as e:
        print(f"❌ CRUD: Error in create_or_get_google_user: {e}")
        db.rollback()
        raise e

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not user.password:  # Google OAuth user without password
        return False
    if not verify_password(password, user.password):
        return False
    return user

# Project CRUD operations
def create_project(db: Session, project: ProjectCreate):
    db_project = Project(
        name=project.name,
        description=project.description
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()

def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def update_project(db: Session, project_id: int, project: ProjectCreate):
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return None
    
    db_project.name = project.name
    db_project.description = project.description
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return False
    
    db.delete(db_project)
    db.commit()
    return True

# Task CRUD operations
def create_task(db: Session, task: TaskCreate):
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        assignee=task.assignee,
        due_date=task.due_date,
        project_id=task.project_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).offset(skip).limit(limit).all()

def get_task_by_id(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(Task).filter(Task.project_id == project_id).offset(skip).limit(limit).all()

def update_task(db: Session, task_id: int, task: TaskCreate):
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return None
    
    db_task.title = task.title
    db_task.description = task.description
    db_task.status = task.status
    db_task.priority = task.priority
    db_task.assignee = task.assignee
    db_task.due_date = task.due_date
    
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True 