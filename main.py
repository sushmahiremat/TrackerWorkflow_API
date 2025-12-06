import time
import logging
import os
import shutil
import re
from typing import Optional
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base, Notification
from schemas import UserCreate, UserLogin, UserResponse, Token, ProjectCreate, ProjectResponse, TaskCreate, TaskResponse, GoogleLogin, CommentCreate, CommentResponse, AttachmentCreate, AttachmentResponse, NotificationCreate, NotificationResponse, TeamCreate, TeamResponse, TeamMemberCreate, TeamMemberResponse, ActivityCreate, ActivityResponse
from crud import create_user, authenticate_user, create_or_get_google_user, create_project, get_projects, get_project_by_id, update_project, delete_project, create_task, get_tasks, get_task_by_id, get_tasks_by_project, update_task, delete_task, create_comment, get_comments_by_task, get_comment_by_id, update_comment, delete_comment, create_attachment, get_attachments_by_task, get_attachment_by_id, delete_attachment, create_notification, get_notifications_by_user, get_unread_notifications_count, get_notification_by_id, mark_notification_as_read, mark_all_notifications_as_read, delete_notification, create_team, get_teams, get_team_by_id, get_teams_by_user, update_team, delete_team, add_team_member, get_team_members, get_team_member, update_member_status, update_member_role, remove_team_member, create_activity, get_activities, get_activity_by_id
from models import NotificationType, TeamRole, MemberStatus, ActivityType
from utils import parse_mentions
from auth import create_access_token, get_current_user
from google_auth import google_auth_service
from config import settings
from models import User
from ai_service import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified successfully")
except Exception as e:
    logger.warning(f"⚠️  Could not create database tables at startup: {str(e)}")
    logger.info("Tables will be created on first database connection")

app = FastAPI(title="TrackerWorkflow API", version="1.0.0")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    logger.info(f"Created uploads directory: {UPLOAD_DIR}")

# Mount static files for serving uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS middleware - Configuration for both development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Development frontend URL
        "https://tracker-workflow.vercel.app",  # Production Vercel URL
        "https://*.vercel.app",  # Any Vercel subdomain
        "https://y55dfkjshm.us-west-2.awsapprunner.com",  # Frontend App Runner URL
        "https://*.awsapprunner.com"  # Any App Runner subdomain
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
    try:
        projects = get_projects(db=db)
        logger.info(f"📦 API: Retrieved {len(projects)} projects from database")
        # Log first project details if any exist
        if projects:
            logger.info(f"📦 API: First project example: id={projects[0].id}, name={projects[0].name}")
        else:
            logger.info("📦 API: No projects found in database")
        return projects
    except Exception as e:
        logger.error(f"❌ API: Error getting projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving projects: {str(e)}"
        )

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
def create_new_task(task: TaskCreate, user_name: str = "Anonymous", db: Session = Depends(get_db)):
    """Create a new task"""
    new_task = create_task(db=db, task=task)
    
    # Parse @mentions from description
    mentions = []
    if task.description:
        mentions = parse_mentions(task.description)
    
    # Create notification if task has an assignee
    if new_task.assignee:
        logger.info(f"📬 Creating notification for new task assignment: user_name={new_task.assignee}, task_id={new_task.id}")
        notification = NotificationCreate(
            type=NotificationType.TASK_ASSIGNED,
            title=f"New Task Assigned: {new_task.title}",
            message=f"You have been assigned to a new task '{new_task.title}'.",
            user_name=new_task.assignee,
            task_id=new_task.id,
            project_id=new_task.project_id
        )
        created_notification = create_notification(db=db, notification=notification)
        logger.info(f"✅ Notification created: id={created_notification.id}")
    
    # Create notifications for @mentions
    for mentioned_user in mentions:
        if mentioned_user != user_name:  # Don't notify yourself
            logger.info(f"📬 Creating mention notification: user_name={mentioned_user}, task_id={new_task.id}")
            mention_notification = NotificationCreate(
                type=NotificationType.MENTION,
                title=f"You were mentioned in: {new_task.title}",
                message=f"{user_name} mentioned you in task '{new_task.title}': {task.description[:100]}...",
                user_name=mentioned_user,
                task_id=new_task.id,
                project_id=new_task.project_id
            )
            create_notification(db=db, notification=mention_notification)
    
    # Create activity log
    project = get_project_by_id(db=db, project_id=new_task.project_id)
    activity = ActivityCreate(
        type=ActivityType.TASK_CREATED,
        description=f"{user_name} created task '{new_task.title}'",
        user_name=user_name,
        project_id=new_task.project_id,
        task_id=new_task.id,
        team_id=None  # team_id temporarily removed from Project model
    )
    create_activity(db=db, activity=activity)
    
    return new_task

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
    # Get the existing task to check for changes
    existing_task = get_task_by_id(db=db, task_id=task_id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if assignee changed
    old_assignee = existing_task.assignee
    new_assignee = task.assignee
    
    updated_task = update_task(db=db, task_id=task_id, task=task)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Parse @mentions from description
    mentions = []
    if updated_task.description:
        mentions = parse_mentions(updated_task.description)
    
    # Create notification if assignee changed and new assignee is set
    if new_assignee and new_assignee != old_assignee:
        logger.info(f"📬 Creating notification for task assignment: user_name={new_assignee}, task_id={updated_task.id}")
        notification = NotificationCreate(
            type=NotificationType.TASK_ASSIGNED,
            title=f"Task Assigned: {updated_task.title}",
            message=f"You have been assigned to the task '{updated_task.title}' in project.",
            user_name=new_assignee,
            task_id=updated_task.id,
            project_id=updated_task.project_id
        )
        created_notification = create_notification(db=db, notification=notification)
        logger.info(f"✅ Notification created: id={created_notification.id}")
    
    # Create notifications for @mentions
    for mentioned_user in mentions:
        if mentioned_user != user_name and mentioned_user != new_assignee:  # Don't notify yourself or the assignee
            logger.info(f"📬 Creating mention notification: user_name={mentioned_user}, task_id={updated_task.id}")
            mention_notification = NotificationCreate(
                type=NotificationType.MENTION,
                title=f"You were mentioned in: {updated_task.title}",
                message=f"{user_name} mentioned you in task '{updated_task.title}': {updated_task.description[:100]}...",
                user_name=mentioned_user,
                task_id=updated_task.id,
                project_id=updated_task.project_id
            )
            create_notification(db=db, notification=mention_notification)
    
    # Create activity log for task update
    project = get_project_by_id(db=db, project_id=updated_task.project_id)
    activity_description = f"{user_name} updated task '{updated_task.title}'"
    activity_metadata = {}
    
    if task.status != existing_task.status:
        activity_description += f" (status changed from {existing_task.status} to {task.status})"
        activity_metadata["old_status"] = existing_task.status
        activity_metadata["new_status"] = task.status
    
    if new_assignee != old_assignee:
        activity_description += f" (assignee changed from {old_assignee or 'Unassigned'} to {new_assignee or 'Unassigned'})"
        activity_metadata["old_assignee"] = old_assignee
        activity_metadata["new_assignee"] = new_assignee
    
    activity = ActivityCreate(
        type=ActivityType.TASK_UPDATED,
        description=activity_description,
        user_name=user_name,
        project_id=updated_task.project_id,
        task_id=updated_task.id,
        team_id=None,  # team_id temporarily removed from Project model
        activity_metadata=activity_metadata
    )
    create_activity(db=db, activity=activity)
    
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_existing_task(task_id: int, user_name: str = "Anonymous", db: Session = Depends(get_db)):
    """Delete a task"""
    task = get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    project = get_project_by_id(db=db, project_id=task.project_id)
    
    success = delete_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Create activity log
    activity = ActivityCreate(
        type=ActivityType.TASK_DELETED,
        description=f"{user_name} deleted task '{task.title}'",
        user_name=user_name,
        project_id=task.project_id,
        team_id=None  # team_id temporarily removed from Project model
    )
    create_activity(db=db, activity=activity)
    
    return {"message": "Task deleted successfully"}

# Comment endpoints
@app.post("/tasks/{task_id}/comments", response_model=CommentResponse)
def create_task_comment(task_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    """Create a new comment for a task"""
    # Verify task exists
    task = get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Create comment with task_id from path
    comment_data = CommentCreate(
        content=comment.content,
        task_id=task_id,  # Use task_id from URL path
        user_name=comment.user_name
    )
    return create_comment(db=db, comment=comment_data)

@app.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
def get_task_comments(task_id: int, db: Session = Depends(get_db)):
    """Get all comments for a task"""
    # Verify task exists
    task = get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return get_comments_by_task(db=db, task_id=task_id)

@app.put("/comments/{comment_id}", response_model=CommentResponse)
def update_task_comment(comment_id: int, request: dict, db: Session = Depends(get_db)):
    """Update a comment"""
    content = request.get("content", "")
    updated_comment = update_comment(db=db, comment_id=comment_id, content=content)
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return updated_comment

@app.delete("/comments/{comment_id}")
def delete_task_comment(comment_id: int, db: Session = Depends(get_db)):
    """Delete a comment"""
    success = delete_comment(db=db, comment_id=comment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return {"message": "Comment deleted successfully"}

# Attachment endpoints
@app.post("/tasks/{task_id}/attachments", response_model=AttachmentResponse)
async def upload_task_attachment(
    task_id: int,
    file: UploadFile = File(...),
    user_name: str = None,
    db: Session = Depends(get_db)
):
    """Upload an attachment for a task"""
    # Verify task exists
    task = get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Create task-specific directory
    task_upload_dir = os.path.join(UPLOAD_DIR, f"task_{task_id}")
    if not os.path.exists(task_upload_dir):
        os.makedirs(task_upload_dir)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(task_upload_dir, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create attachment record
        attachment_data = AttachmentCreate(
            file_name=file.filename,
            file_path=f"task_{task_id}/{unique_filename}",
            file_size=file_size,
            file_type=file.content_type,
            task_id=task_id,
            user_name=user_name
        )
        
        return create_attachment(db=db, attachment=attachment_data)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

@app.get("/tasks/{task_id}/attachments", response_model=list[AttachmentResponse])
def get_task_attachments(task_id: int, db: Session = Depends(get_db)):
    """Get all attachments for a task"""
    # Verify task exists
    task = get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return get_attachments_by_task(db=db, task_id=task_id)

@app.get("/attachments/{attachment_id}/download")
def download_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """Download an attachment file"""
    attachment = get_attachment_by_id(db=db, attachment_id=attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    file_path = os.path.join(UPLOAD_DIR, attachment.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=attachment.file_name,
        media_type=attachment.file_type or "application/octet-stream"
    )

@app.delete("/attachments/{attachment_id}")
def delete_task_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """Delete an attachment"""
    attachment = get_attachment_by_id(db=db, attachment_id=attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Delete file from filesystem
    file_path = os.path.join(UPLOAD_DIR, attachment.file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
    
    # Delete from database
    success = delete_attachment(db=db, attachment_id=attachment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    return {"message": "Attachment deleted successfully"}

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

# Notification endpoints
@app.post("/notifications", response_model=NotificationResponse)
def create_notification_endpoint(notification: NotificationCreate, db: Session = Depends(get_db)):
    """Create a new notification"""
    return create_notification(db=db, notification=notification)

@app.get("/notifications/user/{user_name}", response_model=list[NotificationResponse])
def get_user_notifications(user_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all notifications for a user"""
    return get_notifications_by_user(db=db, user_name=user_name, skip=skip, limit=limit)

@app.get("/notifications/user/{user_name}/unread/count")
def get_unread_notifications_count_endpoint(user_name: str, db: Session = Depends(get_db)):
    """Get count of unread notifications for a user"""
    count = get_unread_notifications_count(db=db, user_name=user_name)
    return {"count": count}

@app.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    """Mark a notification as read"""
    notification = mark_notification_as_read(db=db, notification_id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification

@app.put("/notifications/user/{user_name}/read-all")
def mark_all_notifications_read(user_name: str, db: Session = Depends(get_db)):
    """Mark all notifications as read for a user"""
    mark_all_notifications_as_read(db=db, user_name=user_name)
    return {"message": "All notifications marked as read"}

@app.delete("/notifications/{notification_id}")
def delete_notification_endpoint(notification_id: int, db: Session = Depends(get_db)):
    """Delete a notification"""
    success = delete_notification(db=db, notification_id=notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"message": "Notification deleted successfully"}

# Team endpoints
@app.post("/teams", response_model=TeamResponse)
def create_new_team(team: TeamCreate, user_name: str = "Anonymous", db: Session = Depends(get_db)):
    """Create a new team"""
    return create_team(db=db, team=team, created_by=user_name)

@app.get("/teams", response_model=list[TeamResponse])
def get_all_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all teams"""
    return get_teams(db=db, skip=skip, limit=limit)

@app.get("/teams/user/{user_name}", response_model=list[TeamResponse])
def get_user_teams(user_name: str, db: Session = Depends(get_db)):
    """Get all teams for a user"""
    return get_teams_by_user(db=db, user_name=user_name)

@app.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a specific team"""
    team = get_team_by_id(db=db, team_id=team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return team

@app.put("/teams/{team_id}", response_model=TeamResponse)
def update_existing_team(team_id: int, team: TeamCreate, db: Session = Depends(get_db)):
    """Update a team"""
    updated_team = update_team(db=db, team_id=team_id, team=team)
    if not updated_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return updated_team

@app.delete("/teams/{team_id}")
def delete_existing_team(team_id: int, db: Session = Depends(get_db)):
    """Delete a team"""
    success = delete_team(db=db, team_id=team_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return {"message": "Team deleted successfully"}

# TeamMember endpoints
@app.post("/teams/{team_id}/members", response_model=TeamMemberResponse)
def add_member_to_team(team_id: int, member: TeamMemberCreate, db: Session = Depends(get_db)):
    """Add a member to a team"""
    member.team_id = team_id
    return add_team_member(db=db, member=member)

@app.get("/teams/{team_id}/members", response_model=list[TeamMemberResponse])
def get_team_members_endpoint(team_id: int, db: Session = Depends(get_db)):
    """Get all members of a team"""
    return get_team_members(db=db, team_id=team_id)

@app.put("/teams/{team_id}/members/{user_name}/status")
def update_member_status_endpoint(team_id: int, user_name: str, status: MemberStatus, db: Session = Depends(get_db)):
    """Update a member's status"""
    member = update_member_status(db=db, team_id=team_id, user_name=user_name, status=status)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    return member

@app.put("/teams/{team_id}/members/{user_name}/role")
def update_member_role_endpoint(team_id: int, user_name: str, role: TeamRole, db: Session = Depends(get_db)):
    """Update a member's role"""
    member = update_member_role(db=db, team_id=team_id, user_name=user_name, role=role)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    return member

@app.delete("/teams/{team_id}/members/{user_name}")
def remove_member_from_team(team_id: int, user_name: str, db: Session = Depends(get_db)):
    """Remove a member from a team"""
    success = remove_team_member(db=db, team_id=team_id, user_name=user_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    return {"message": "Member removed successfully"}

# Activity endpoints
@app.post("/activities", response_model=ActivityResponse)
def create_activity_endpoint(activity: ActivityCreate, db: Session = Depends(get_db)):
    """Create a new activity"""
    return create_activity(db=db, activity=activity)

@app.get("/activities", response_model=list[ActivityResponse])
def get_activities_endpoint(team_id: Optional[int] = None, project_id: Optional[int] = None, 
                           task_id: Optional[int] = None, skip: int = 0, limit: int = 100, 
                           db: Session = Depends(get_db)):
    """Get activities with optional filters"""
    return get_activities(db=db, team_id=team_id, project_id=project_id, task_id=task_id, skip=skip, limit=limit)

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