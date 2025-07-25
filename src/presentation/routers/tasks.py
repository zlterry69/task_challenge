from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from src.application.auth_service import get_current_user
from src.application.dto import (
    CompletionStatsDTO,
    TaskCreateDTO,
    TaskResponseDTO,
    TaskStatusUpdateDTO,
    TaskUpdateDTO,
)
from src.application.services import NotificationService
from src.domain.entities import TaskPriority, TaskStatus
from src.infrastructure.database import (
    SessionLocal,
    TaskListModel,
    TaskModel,
    UserModel,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _is_task_overdue(task: TaskModel) -> bool:
    """Check if a task is overdue based on due_date and current time"""
    if not task.due_date:
        return False  # No due date = not overdue

    if task.status == TaskStatus.COMPLETED:
        return False  # Completed tasks are never overdue

    return datetime.utcnow() > task.due_date


@router.post("/", response_model=TaskResponseDTO)
async def create_task(
    task_in: TaskCreateDTO,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Verify task list exists and user owns it
    task_list = (
        db.query(TaskListModel)
        .filter(
            TaskListModel.id == task_in.task_list_id, TaskListModel.owner_id == user.id
        )
        .first()
    )
    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")

    task = TaskModel(
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        task_list_id=task_in.task_list_id,
        assigned_to=task_in.assigned_to,
        due_date=task_in.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Query the task again with assignee name to ensure all fields are properly loaded
    result = (
        db.query(TaskModel, UserModel.full_name.label("assignee_name"))
        .outerjoin(UserModel, TaskModel.assigned_to == UserModel.id)
        .filter(TaskModel.id == task.id)
        .first()
    )

    created_task, assignee_name = result if result else (task, None)

    # 📧 FICTITIOUS EMAIL: Send assignment notification if task is assigned
    if created_task.assigned_to:
        assignee = (
            db.query(UserModel).filter(UserModel.id == created_task.assigned_to).first()
        )
        if assignee:
            notification_service = NotificationService()
            await notification_service.send_task_assignment_notification(
                created_task, assignee
            )

    return TaskResponseDTO(
        id=created_task.id,
        title=created_task.title,
        description=created_task.description,
        status=created_task.status,
        priority=created_task.priority,
        task_list_id=created_task.task_list_id,
        assigned_to=created_task.assigned_to,
        created_at=created_task.created_at,
        updated_at=created_task.updated_at,
        due_date=created_task.due_date,
        is_overdue=_is_task_overdue(created_task),
        assignee_name=assignee_name,
    )


@router.get("/stats", response_model=CompletionStatsDTO)
def get_task_completion_stats(
    task_list_id: Optional[int] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get completion statistics for tasks with optional filters"""

    # Base query - only tasks from user's task lists
    base_query = (
        db.query(TaskModel)
        .join(TaskListModel)
        .filter(TaskListModel.owner_id == user.id)
    )

    # Apply filters
    if task_list_id:
        base_query = base_query.filter(TaskModel.task_list_id == task_list_id)
    if status:
        base_query = base_query.filter(TaskModel.status == status)
    if priority:
        base_query = base_query.filter(TaskModel.priority == priority)

    # Get statistics
    stats = base_query.with_entities(
        func.count(TaskModel.id).label("total"),
        func.sum(case((TaskModel.status == TaskStatus.COMPLETED, 1), else_=0)).label(
            "completed"
        ),
        func.sum(case((TaskModel.status == TaskStatus.PENDING, 1), else_=0)).label(
            "pending"
        ),
        func.sum(case((TaskModel.status == TaskStatus.IN_PROGRESS, 1), else_=0)).label(
            "in_progress"
        ),
        func.sum(case((TaskModel.status == TaskStatus.CANCELLED, 1), else_=0)).label(
            "cancelled"
        ),
    ).first()

    total_tasks = stats.total or 0
    completed_tasks = stats.completed or 0
    pending_tasks = stats.pending or 0
    in_progress_tasks = stats.in_progress or 0
    cancelled_tasks = stats.cancelled or 0

    # Calculate completion percentage
    completion_percentage = 0.0
    if total_tasks > 0:
        completion_percentage = (completed_tasks / total_tasks) * 100

    return CompletionStatsDTO(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        cancelled_tasks=cancelled_tasks,
        completion_percentage=round(completion_percentage, 1),
    )


@router.get("/", response_model=List[TaskResponseDTO])
def get_tasks(
    task_list_id: Optional[int] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Join with UserModel to get assignee name
    query = (
        db.query(TaskModel, UserModel.full_name.label("assignee_name"))
        .join(TaskListModel, TaskModel.task_list_id == TaskListModel.id)
        .outerjoin(UserModel, TaskModel.assigned_to == UserModel.id)
        .filter(TaskListModel.owner_id == user.id)
    )

    if task_list_id:
        query = query.filter(TaskModel.task_list_id == task_list_id)
    if status:
        query = query.filter(TaskModel.status == status)
    if priority:
        query = query.filter(TaskModel.priority == priority)

    results = query.all()
    return [
        TaskResponseDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            task_list_id=task.task_list_id,
            assigned_to=task.assigned_to,
            created_at=task.created_at,
            updated_at=task.updated_at,
            due_date=task.due_date,
            is_overdue=_is_task_overdue(task),
            assignee_name=assignee_name,
        )
        for task, assignee_name in results
    ]


@router.patch("/{task_id}/status", response_model=TaskResponseDTO)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdateDTO,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = (
        db.query(TaskModel)
        .join(TaskListModel)
        .filter(TaskModel.id == task_id, TaskListModel.owner_id == user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_status = task.status
    task.status = status_update.status
    db.commit()
    db.refresh(task)

    # 📧 FICTITIOUS EMAIL: Send completion notification if task was just completed
    if (
        old_status != TaskStatus.COMPLETED
        and status_update.status == TaskStatus.COMPLETED
    ):
        # Get task list owner
        task_list = (
            db.query(TaskListModel)
            .filter(TaskListModel.id == task.task_list_id)
            .first()
        )
        if task_list:
            owner = (
                db.query(UserModel).filter(UserModel.id == task_list.owner_id).first()
            )
            if owner:
                notification_service = NotificationService()
                await notification_service.send_task_completion_notification(
                    task, owner
                )

    # Query with assignee name
    result = (
        db.query(TaskModel, UserModel.full_name.label("assignee_name"))
        .outerjoin(UserModel, TaskModel.assigned_to == UserModel.id)
        .filter(TaskModel.id == task.id)
        .first()
    )

    updated_task, assignee_name = result if result else (task, None)

    return TaskResponseDTO(
        id=updated_task.id,
        title=updated_task.title,
        description=updated_task.description,
        status=updated_task.status,
        priority=updated_task.priority,
        task_list_id=updated_task.task_list_id,
        assigned_to=updated_task.assigned_to,
        created_at=updated_task.created_at,
        updated_at=updated_task.updated_at,
        due_date=updated_task.due_date,
        is_overdue=_is_task_overdue(updated_task),
        assignee_name=assignee_name,
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    """Delete a specific task"""
    task = (
        db.query(TaskModel)
        .join(TaskListModel)
        .filter(TaskModel.id == task_id, TaskListModel.owner_id == user.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_title = task.title
    db.delete(task)
    db.commit()

    return {"message": f"Task '{task_title}' deleted successfully"}


@router.put("/{task_id}", response_model=TaskResponseDTO)
def update_task(
    task_id: int,
    task_update: TaskUpdateDTO,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Update a task completely"""
    task = (
        db.query(TaskModel)
        .join(TaskListModel)
        .filter(TaskModel.id == task_id, TaskListModel.owner_id == user.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields if provided
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.assigned_to is not None:
        task.assigned_to = task_update.assigned_to
    if task_update.due_date is not None:
        task.due_date = task_update.due_date

    db.commit()
    db.refresh(task)

    # Query with assignee name
    result = (
        db.query(TaskModel, UserModel.full_name.label("assignee_name"))
        .outerjoin(UserModel, TaskModel.assigned_to == UserModel.id)
        .filter(TaskModel.id == task.id)
        .first()
    )

    updated_task, assignee_name = result if result else (task, None)

    return TaskResponseDTO(
        id=updated_task.id,
        title=updated_task.title,
        description=updated_task.description,
        status=updated_task.status,
        priority=updated_task.priority,
        task_list_id=updated_task.task_list_id,
        assigned_to=updated_task.assigned_to,
        created_at=updated_task.created_at,
        updated_at=updated_task.updated_at,
        due_date=updated_task.due_date,
        is_overdue=_is_task_overdue(updated_task),
        assignee_name=assignee_name,
    )
