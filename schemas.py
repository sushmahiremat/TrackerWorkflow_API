from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import TaskStatus, TaskPriority

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

class TaskCreate(TaskBase):
    project_id: int

class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 