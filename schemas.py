from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import TaskStatus, TaskPriority, NotificationType, TeamRole, MemberStatus, ActivityType

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class GoogleLogin(BaseModel):
    id_token: str

class GoogleUserInfo(BaseModel):
    sub: str  # Google user ID
    email: EmailStr
    name: str
    picture: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    auth_provider: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = []

class TaskCreate(TaskBase):
    project_id: int

class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Comment schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    task_id: Optional[int] = None
    user_name: Optional[str] = None

class CommentResponse(CommentBase):
    id: int
    task_id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Attachment schemas
class AttachmentBase(BaseModel):
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None

class AttachmentCreate(AttachmentBase):
    task_id: int
    user_name: Optional[str] = None

class AttachmentResponse(AttachmentBase):
    id: int
    task_id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Notification schemas
class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    user_name: str
    task_id: Optional[int] = None
    project_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Team schemas
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# TeamMember schemas
class TeamMemberBase(BaseModel):
    user_name: str
    user_email: Optional[str] = None
    role: TeamRole = TeamRole.MEMBER
    status: MemberStatus = MemberStatus.OFFLINE
    avatar_url: Optional[str] = None

class TeamMemberCreate(TeamMemberBase):
    team_id: Optional[int] = None  # Optional since it's set from path parameter in the endpoint

class TeamMemberResponse(TeamMemberBase):
    id: int
    team_id: int
    joined_at: datetime
    last_seen: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Activity schemas
class ActivityBase(BaseModel):
    type: ActivityType
    description: str
    user_name: str
    user_avatar: Optional[str] = None
    team_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    activity_metadata: Optional[dict] = None  # Renamed from 'metadata' as it's reserved in SQLAlchemy

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 