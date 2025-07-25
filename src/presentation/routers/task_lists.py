from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from src.application.auth_service import get_current_user
from src.application.dto import (
    TaskListCreateDTO,
    TaskListResponseDTO,
    TaskListUpdateDTO,
)
from src.domain.entities import TaskStatus
from src.infrastructure.database import SessionLocal, TaskListModel, TaskModel

router = APIRouter(prefix="/api/task-lists", tags=["task-lists"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TaskListResponseDTO)
def create_task_list(
    task_list_in: TaskListCreateDTO,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task_list = TaskListModel(
        name=task_list_in.name, description=task_list_in.description, owner_id=user.id
    )
    db.add(task_list)
    db.commit()
    db.refresh(task_list)

    return TaskListResponseDTO(
        id=task_list.id,
        name=task_list.name,
        description=task_list.description,
        owner_id=task_list.owner_id,
        created_at=task_list.created_at,
        updated_at=task_list.updated_at,
        completion_percentage=0.0,
        task_count=0,
    )


@router.get("/", response_model=List[TaskListResponseDTO])
def get_task_lists(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Get task lists with task counts and completion stats
    query = (
        db.query(
            TaskListModel,
            func.count(TaskModel.id).label("total_tasks"),
            func.sum(
                case((TaskModel.status == TaskStatus.COMPLETED, 1), else_=0)
            ).label("completed_tasks"),
        )
        .outerjoin(TaskModel, TaskListModel.id == TaskModel.task_list_id)
        .filter(TaskListModel.owner_id == user.id)
        .group_by(TaskListModel.id)
    )

    results = query.all()

    task_lists_response = []
    for task_list, total_tasks, completed_tasks in results:
        # Calculate completion percentage
        completion_percentage = 0.0
        if total_tasks and total_tasks > 0:
            completed_tasks = completed_tasks or 0
            completion_percentage = (completed_tasks / total_tasks) * 100

        task_lists_response.append(
            TaskListResponseDTO(
                id=task_list.id,
                name=task_list.name,
                description=task_list.description,
                owner_id=task_list.owner_id,
                created_at=task_list.created_at,
                updated_at=task_list.updated_at,
                completion_percentage=round(completion_percentage, 1),
                task_count=total_tasks or 0,
            )
        )

    return task_lists_response


@router.get("/{task_list_id}", response_model=TaskListResponseDTO)
def get_task_list(
    task_list_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    # Get task list with completion stats
    result = (
        db.query(
            TaskListModel,
            func.count(TaskModel.id).label("total_tasks"),
            func.sum(
                case((TaskModel.status == TaskStatus.COMPLETED, 1), else_=0)
            ).label("completed_tasks"),
        )
        .outerjoin(TaskModel, TaskListModel.id == TaskModel.task_list_id)
        .filter(TaskListModel.id == task_list_id, TaskListModel.owner_id == user.id)
        .group_by(TaskListModel.id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Task list not found")

    task_list, total_tasks, completed_tasks = result

    # Calculate completion percentage
    completion_percentage = 0.0
    if total_tasks and total_tasks > 0:
        completed_tasks = completed_tasks or 0
        completion_percentage = (completed_tasks / total_tasks) * 100

    return TaskListResponseDTO(
        id=task_list.id,
        name=task_list.name,
        description=task_list.description,
        owner_id=task_list.owner_id,
        created_at=task_list.created_at,
        updated_at=task_list.updated_at,
        completion_percentage=round(completion_percentage, 1),
        task_count=total_tasks or 0,
    )


@router.delete("/{task_list_id}")
def delete_task_list(
    task_list_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    """Delete a task list and all its tasks"""
    task_list = (
        db.query(TaskListModel)
        .filter(TaskListModel.id == task_list_id, TaskListModel.owner_id == user.id)
        .first()
    )

    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")

    # Delete the task list (tasks will be deleted by cascade)
    db.delete(task_list)
    db.commit()

    return {"message": f"Task list '{task_list.name}' deleted successfully"}


@router.put("/{task_list_id}", response_model=TaskListResponseDTO)
def update_task_list(
    task_list_id: int,
    task_list_update: TaskListUpdateDTO,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Update a task list"""
    task_list = (
        db.query(TaskListModel)
        .filter(TaskListModel.id == task_list_id, TaskListModel.owner_id == user.id)
        .first()
    )

    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")

    # Update fields if provided
    if task_list_update.name is not None:
        task_list.name = task_list_update.name
    if task_list_update.description is not None:
        task_list.description = task_list_update.description

    db.commit()
    db.refresh(task_list)

    # Get updated stats
    result = (
        db.query(
            TaskListModel,
            func.count(TaskModel.id).label("total_tasks"),
            func.sum(
                case((TaskModel.status == TaskStatus.COMPLETED, 1), else_=0)
            ).label("completed_tasks"),
        )
        .outerjoin(TaskModel, TaskListModel.id == TaskModel.task_list_id)
        .filter(TaskListModel.id == task_list_id, TaskListModel.owner_id == user.id)
        .group_by(TaskListModel.id)
        .first()
    )

    updated_task_list, total_tasks, completed_tasks = (
        result if result else (task_list, 0, 0)
    )

    # Calculate completion percentage
    completion_percentage = 0.0
    if total_tasks and total_tasks > 0:
        completed_tasks = completed_tasks or 0
        completion_percentage = (completed_tasks / total_tasks) * 100

    return TaskListResponseDTO(
        id=updated_task_list.id,
        name=updated_task_list.name,
        description=updated_task_list.description,
        owner_id=updated_task_list.owner_id,
        created_at=updated_task_list.created_at,
        updated_at=updated_task_list.updated_at,
        completion_percentage=round(completion_percentage, 1),
        task_count=total_tasks or 0,
    )
