"""Domain entities for the Task Challenge application."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(BaseModel):
    id: Optional[int] = None
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100)
    hashed_password: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskList(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    owner_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    tasks: List["Task"] = Field(default_factory=list)
    owner: Optional[User] = None

    def calculate_completion_percentage(self) -> float:
        if not self.tasks:
            return 0.0

        completed_tasks = sum(
            1 for task in self.tasks if task.status == TaskStatus.COMPLETED
        )
        return (completed_tasks / len(self.tasks)) * 100.0

    class Config:
        from_attributes = True


class Task(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    task_list_id: int
    assigned_to: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

    task_list: Optional[TaskList] = None
    assignee: Optional[User] = None

    def is_overdue(self) -> bool:
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status != TaskStatus.COMPLETED

    def can_be_assigned_to(self, user_id: int) -> bool:
        return user_id > 0

    def mark_as_completed(self) -> None:
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def change_priority(self, new_priority: TaskPriority) -> None:
        self.priority = new_priority
        self.updated_at = datetime.utcnow()

    class Config:
        from_attributes = True


TaskList.model_rebuild()
Task.model_rebuild()
