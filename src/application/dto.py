from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.domain.entities import TaskPriority, TaskStatus


class UserCreateDTO(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str = Field(..., min_length=8)


class UserUpdateDTO(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponseDTO(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None


class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str
    user: UserResponseDTO


class TaskListCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TaskListUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TaskListResponseDTO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completion_percentage: float = 0.0
    task_count: int = 0


class TaskCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM
    task_list_id: int
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdateDTO(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskStatusUpdateDTO(BaseModel):
    status: TaskStatus


class TaskResponseDTO(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    task_list_id: int
    assigned_to: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    is_overdue: bool = False
    assignee_name: Optional[str] = None


class TaskFilterDTO(BaseModel):
    task_list_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[int] = None
    overdue_only: bool = False


class CompletionStatsDTO(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    cancelled_tasks: int
    completion_percentage: float
