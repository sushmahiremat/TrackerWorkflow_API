import time
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import User, Project, Task, Comment, Attachment, Notification, NotificationType, Team, TeamMember, Activity, TeamRole, MemberStatus, ActivityType
from schemas import UserCreate, ProjectCreate, TaskCreate, GoogleUserInfo, CommentCreate, AttachmentCreate, NotificationCreate, TeamCreate, TeamMemberCreate, ActivityCreate
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
    try:
        projects = db.query(Project).offset(skip).limit(limit).all()
        print(f"📦 CRUD: Retrieved {len(projects)} projects from database")
        return projects
    except Exception as e:
        print(f"❌ CRUD: Error retrieving projects: {e}")
        raise

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
        tags=task.tags if task.tags else [],
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
    db_task.tags = task.tags if task.tags is not None else (db_task.tags if db_task.tags else [])
    
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

# Comment CRUD operations
def create_comment(db: Session, comment: CommentCreate):
    db_comment = Comment(
        content=comment.content,
        task_id=comment.task_id,
        user_name=comment.user_name
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_by_task(db: Session, task_id: int):
    return db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at.desc()).all()

def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()

def update_comment(db: Session, comment_id: int, content: str):
    db_comment = get_comment_by_id(db, comment_id)
    if not db_comment:
        return None
    
    db_comment.content = content
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    db_comment = get_comment_by_id(db, comment_id)
    if not db_comment:
        return False
    
    db.delete(db_comment)
    db.commit()
    return True

# Attachment CRUD operations
def create_attachment(db: Session, attachment: AttachmentCreate):
    db_attachment = Attachment(
        file_name=attachment.file_name,
        file_path=attachment.file_path,
        file_size=attachment.file_size,
        file_type=attachment.file_type,
        task_id=attachment.task_id,
        user_name=attachment.user_name
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

def get_attachments_by_task(db: Session, task_id: int):
    return db.query(Attachment).filter(Attachment.task_id == task_id).order_by(Attachment.created_at.desc()).all()

def get_attachment_by_id(db: Session, attachment_id: int):
    return db.query(Attachment).filter(Attachment.id == attachment_id).first()

def delete_attachment(db: Session, attachment_id: int):
    db_attachment = get_attachment_by_id(db, attachment_id)
    if not db_attachment:
        return False
    
    db.delete(db_attachment)
    db.commit()
    return True

# Notification CRUD operations
def create_notification(db: Session, notification: NotificationCreate):
    db_notification = Notification(
        type=notification.type,
        title=notification.title,
        message=notification.message,
        user_name=notification.user_name,
        task_id=notification.task_id,
        project_id=notification.project_id,
        is_read=False
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_by_user(db: Session, user_name: str, skip: int = 0, limit: int = 100):
    notifications = db.query(Notification).filter(
        Notification.user_name == user_name
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    print(f"📬 CRUD: Found {len(notifications)} notifications for user: {user_name}")
    return notifications

def get_unread_notifications_count(db: Session, user_name: str):
    return db.query(Notification).filter(
        Notification.user_name == user_name,
        Notification.is_read == False
    ).count()

def get_notification_by_id(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()

def mark_notification_as_read(db: Session, notification_id: int):
    db_notification = get_notification_by_id(db, notification_id)
    if not db_notification:
        return False
    
    db_notification.is_read = True
    db.commit()
    db.refresh(db_notification)
    return db_notification

def mark_all_notifications_as_read(db: Session, user_name: str):
    db.query(Notification).filter(
        Notification.user_name == user_name,
        Notification.is_read == False
    ).update({Notification.is_read: True})
    db.commit()
    return True

def delete_notification(db: Session, notification_id: int):
    db_notification = get_notification_by_id(db, notification_id)
    if not db_notification:
        return False
    
    db.delete(db_notification)
    db.commit()
    return True

# Team CRUD operations
def create_team(db: Session, team: TeamCreate, created_by: str):
    db_team = Team(
        name=team.name,
        description=team.description,
        created_by=created_by
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    # Add creator as owner
    creator_member = TeamMember(
        team_id=db_team.id,
        user_name=created_by,
        role=TeamRole.OWNER,
        status=MemberStatus.ONLINE
    )
    db.add(creator_member)
    db.commit()
    
    return db_team

def get_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Team).offset(skip).limit(limit).all()

def get_team_by_id(db: Session, team_id: int):
    return db.query(Team).filter(Team.id == team_id).first()

def get_teams_by_user(db: Session, user_name: str):
    return db.query(Team).join(TeamMember).filter(TeamMember.user_name == user_name).all()

def update_team(db: Session, team_id: int, team: TeamCreate):
    db_team = get_team_by_id(db, team_id)
    if not db_team:
        return None
    
    db_team.name = team.name
    db_team.description = team.description
    db.commit()
    db.refresh(db_team)
    return db_team

def delete_team(db: Session, team_id: int):
    db_team = get_team_by_id(db, team_id)
    if not db_team:
        return False
    
    db.delete(db_team)
    db.commit()
    return True

# TeamMember CRUD operations
def add_team_member(db: Session, member: TeamMemberCreate):
    # Check if member already exists
    existing = db.query(TeamMember).filter(
        TeamMember.team_id == member.team_id,
        TeamMember.user_name == member.user_name
    ).first()
    
    if existing:
        return existing
    
    db_member = TeamMember(
        team_id=member.team_id,
        user_name=member.user_name,
        user_email=member.user_email,
        role=member.role,
        status=member.status,
        avatar_url=member.avatar_url
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_team_members(db: Session, team_id: int):
    return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

def get_team_member(db: Session, team_id: int, user_name: str):
    return db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_name == user_name
    ).first()

def update_member_status(db: Session, team_id: int, user_name: str, status: MemberStatus):
    member = get_team_member(db, team_id, user_name)
    if not member:
        return None
    
    member.status = status
    member.last_seen = func.now()
    db.commit()
    db.refresh(member)
    return member

def update_member_role(db: Session, team_id: int, user_name: str, role: TeamRole):
    member = get_team_member(db, team_id, user_name)
    if not member:
        return None
    
    member.role = role
    db.commit()
    db.refresh(member)
    return member

def remove_team_member(db: Session, team_id: int, user_name: str):
    member = get_team_member(db, team_id, user_name)
    if not member:
        return False
    
    db.delete(member)
    db.commit()
    return True

# Activity CRUD operations
def create_activity(db: Session, activity: ActivityCreate):
    db_activity = Activity(
        type=activity.type,
        description=activity.description,
        user_name=activity.user_name,
        user_avatar=activity.user_avatar,
        team_id=activity.team_id,
        project_id=activity.project_id,
        task_id=activity.task_id,
        activity_metadata=activity.activity_metadata
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_activities(db: Session, team_id: Optional[int] = None, project_id: Optional[int] = None, 
                   task_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(Activity)
    
    if team_id:
        query = query.filter(Activity.team_id == team_id)
    if project_id:
        query = query.filter(Activity.project_id == project_id)
    if task_id:
        query = query.filter(Activity.task_id == task_id)
    
    return query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()

def get_activity_by_id(db: Session, activity_id: int):
    return db.query(Activity).filter(Activity.id == activity_id).first() 