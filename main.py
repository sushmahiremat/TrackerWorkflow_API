import time
import logging
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base
from schemas import UserCreate, UserLogin, UserResponse, Token, ProjectCreate, ProjectResponse, TaskCreate, TaskResponse, GoogleLogin
from crud import create_user, authenticate_user, create_or_get_google_user, create_project, get_projects, get_project_by_id, update_project, delete_project, create_task, get_tasks, get_task_by_id, get_tasks_by_project, update_task, delete_task
from auth import create_access_token, get_current_user
from google_auth import google_auth_service
from config import settings
from models import User
from ai_service import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TrackerWorkflow API", version="1.0.0")

# CORS middleware - Configuration for both development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Development frontend URL
        "https://tracker-workflow.vercel.app",  # Production Vercel URL
        "https://*.vercel.app"  # Any Vercel subdomain
    ],
    allow_credentials=True,  # Allow credentials
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return create_user(db=db, user=user)

@app.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/google", response_model=Token)
async def google_login(google_data: GoogleLogin, db: Session = Depends(get_db)):
    """Login with Google OAuth"""
    start_time = time.time()
    print(f"🔐 Backend: Google OAuth login request received at {time.strftime('%H:%M:%S')}")
    print(f"🔑 ID Token length: {len(google_data.id_token) if google_data.id_token else 'No token'}")
    
    try:
        # Step 1: Verify Google token
        step1_start = time.time()
        print("📤 Backend: Verifying Google token...")
        google_user = await google_auth_service.verify_google_token(google_data.id_token)
        step1_time = time.time() - step1_start
        print(f"✅ Backend: Google token verified in {step1_time:.2f}s, user: {google_user.email}")
        
        # Step 2: Create or get user from database
        step2_start = time.time()
        print("👤 Backend: Creating or getting user from database...")
        user = create_or_get_google_user(db, google_user)
        step2_time = time.time() - step2_start
        print(f"✅ Backend: User retrieved/created in {step2_time:.2f}s: {user.email}")
        
        # Step 3: Create access token
        step3_start = time.time()
        print("🎫 Backend: Creating access token...")
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        step3_time = time.time() - step3_start
        print(f"✅ Backend: Access token created in {step3_time:.2f}s")
        
        total_time = time.time() - start_time
        print(f"🎉 Backend: Google OAuth completed successfully in {total_time:.2f}s")
        
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        total_time = time.time() - start_time
        print(f"❌ Backend: Google OAuth error after {total_time:.2f}s: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        total_time = time.time() - start_time
        print(f"❌ Backend: Unexpected error in Google OAuth after {total_time:.2f}s: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during Google OAuth"
        )

@app.get("/auth/google/url")
def get_google_auth_url():
    """Get Google OAuth URL for frontend"""
    auth_url = google_auth_service.get_google_auth_url()
    return {"auth_url": auth_url}

@app.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Project endpoints
@app.post("/projects", response_model=ProjectResponse)
def create_new_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    return create_project(db=db, project=project)

@app.get("/projects", response_model=list[ProjectResponse])
def get_all_projects(db: Session = Depends(get_db)):
    """Get all projects"""
    return get_projects(db=db)

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID"""
    project = get_project_by_id(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@app.put("/projects/{project_id}", response_model=ProjectResponse)
def update_existing_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    """Update an existing project"""
    updated_project = update_project(db=db, project_id=project_id, project=project)
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return updated_project

@app.delete("/projects/{project_id}")
def delete_existing_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    success = delete_project(db=db, project_id=project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return {"message": "Project deleted successfully"}

# Task endpoints
@app.post("/tasks", response_model=TaskResponse)
def create_new_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    return create_task(db=db, task=task)

@app.get("/tasks", response_model=list[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    """Get all tasks"""
    return get_tasks(db=db)

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    task = get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@app.get("/tasks/project/{project_id}", response_model=list[TaskResponse])
def get_tasks_by_project_id(project_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a specific project"""
    return get_tasks_by_project(db=db, project_id=project_id)

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_existing_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    """Update an existing task"""
    updated_task = update_task(db=db, task_id=task_id, task=task)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_existing_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    success = delete_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return {"message": "Task deleted successfully"}

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "TrackerWorkflow API is running!"}

@app.get("/performance")
def get_performance_stats():
    """Get performance statistics"""
    from crud import clear_user_cache
    from google_auth import _token_cache
    
    return {
        "message": "Performance statistics",
        "user_cache_size": len(_user_cache),
        "token_cache_size": len(_token_cache),
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

@app.post("/performance/clear-cache")
def clear_caches():
    """Clear all caches for testing"""
    from crud import clear_user_cache
    from google_auth import _token_cache
    
    _user_cache.clear()
    _token_cache.clear()
    
    return {"message": "All caches cleared successfully"}

# AI endpoints
@app.post("/ai/summarize-task")
async def summarize_task(request: dict):
    """Generate AI-powered task summary and subtasks"""
    try:
        description = request.get("description", "")
        if not description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task description is required"
            )
        
        logger.info(f"AI request received for description: {description[:100]}...")
        
        # Generate AI summary and subtasks
        result = await ai_service.summarize_task(description)
        
        logger.info(f"AI response generated: summary={result.get('summary', 'N/A')[:50]}..., subtasks_count={len(result.get('subtasks', []))}")
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"AI endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service temporarily unavailable"
        )

@app.get("/ai/test")
async def test_ai_service():
    """Test endpoint to verify AI service is working"""
    try:
        test_description = "Build a complete user authentication system with Google SSO and password reset functionality"
        result = await ai_service.summarize_task(test_description)
        
        return {
            "success": True,
            "message": "AI service is working",
            "test_description": test_description,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"AI test error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "AI service test failed"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001) 