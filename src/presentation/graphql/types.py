from datetime import datetime
from enum import Enum
from typing import Optional

import strawberry


@strawberry.enum
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@strawberry.enum
class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@strawberry.type
class User:
    id: int
    email: str
    full_name: Optional[str] = None


@strawberry.type
class TaskList:
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    completion_percentage: float = 0.0
    task_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    task_list_id: int
    assigned_to: Optional[int] = None
    assignee_name: Optional[str] = None
    due_date: Optional[datetime] = None
    is_overdue: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@strawberry.type
class AuthPayload:
    access_token: str
    token_type: str = "bearer"
    user: User


@strawberry.type
class CompletionStats:
    task_list_id: int
    completion_percentage: float
    total_tasks: int
    completed_tasks: int


@strawberry.input
class UserCreateInput:
    email: str
    full_name: Optional[str] = strawberry.field(default=None, name="fullName")
    password: str


@strawberry.input
class UserLoginInput:
    email: str
    password: str


@strawberry.input
class TaskListCreateInput:
    name: str
    description: Optional[str] = None


@strawberry.input
class TaskListUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None


@strawberry.input
class TaskCreateInput:
    """Input for creating tasks"""

    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.PENDING
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    task_list_id: int
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


@strawberry.input
class TaskUpdateInput:
    """Input for updating tasks"""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


@strawberry.input
class TaskFilterInput:
    """Input for filtering tasks following GraphQL best practices"""

    task_list_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


@strawberry.input
class TaskStatusUpdateInput:
    status: TaskStatus
