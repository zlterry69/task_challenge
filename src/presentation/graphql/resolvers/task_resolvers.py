from datetime import datetime
from typing import List, Optional

import strawberry
from sqlalchemy import case, func
from strawberry.types import Info

from src.application.services import NotificationService
from src.domain.entities import TaskPriority as DomainTaskPriority
from src.domain.entities import TaskStatus as DomainTaskStatus
from src.infrastructure.database import TaskListModel, TaskModel, UserModel

from ..context import get_db, require_auth
from ..types import (
    CompletionStats,
    Task,
    TaskCreateInput,
    TaskFilterInput,
    TaskPriority,
    TaskStatus,
    TaskUpdateInput,
)


def _is_task_overdue(task: TaskModel) -> bool:
    """Reuse REST logic for overdue calculation"""
    if not task.due_date:
        return False
    if task.status == DomainTaskStatus.COMPLETED:
        return False
    return datetime.utcnow() > task.due_date


@strawberry.type
class TaskQuery:
    @strawberry.field
    def tasks(self, info: Info, filter: Optional[TaskFilterInput] = None) -> List[Task]:
        """Get tasks for authenticated user with full fields - reuses REST logic"""
        user = require_auth(info)
        db = get_db()
        try:
            # Reuse REST query logic with JOIN for assignee name
            query = (
                db.query(TaskModel, UserModel.full_name.label("assignee_name"))
                .join(TaskListModel, TaskModel.task_list_id == TaskListModel.id)
                .outerjoin(UserModel, TaskModel.assigned_to == UserModel.id)
                .filter(TaskListModel.owner_id == user.id)
            )

            if filter:
                if filter.task_list_id:
                    query = query.filter(TaskModel.task_list_id == filter.task_list_id)
                if filter.status:
                    query = query.filter(TaskModel.status == filter.status.value)
                if filter.priority:
                    query = query.filter(TaskModel.priority == filter.priority.value)

            results = query.all()
            return [
                Task(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    status=TaskStatus(task.status),
                    priority=TaskPriority(task.priority),
                    task_list_id=task.task_list_id,
                    assigned_to=task.assigned_to,
                    assignee_name=assignee_name,
                    due_date=task.due_date,
                    is_overdue=_is_task_overdue(task),
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task, assignee_name in results
            ]
        finally:
            db.close()

    @strawberry.field
    def task(self, id: int, info: Info) -> Optional[Task]:
        """Get specific task with full fields - user must own the task list"""
        user = require_auth(info)
        db = get_db()
        try:
            result = (
                db.query(TaskModel, UserModel.full_name.label("assignee_name"))
                .join(TaskListModel, TaskModel.task_list_id == TaskListModel.id)
                .outerjoin(UserModel, TaskModel.assigned_to == UserModel.id)
                .filter(TaskModel.id == id, TaskListModel.owner_id == user.id)
                .first()
            )

            if not result:
                return None

            task, assignee_name = result
            return Task(
                id=task.id,
                title=task.title,
                description=task.description,
                status=TaskStatus(task.status),
                priority=TaskPriority(task.priority),
                task_list_id=task.task_list_id,
                assigned_to=task.assigned_to,
                assignee_name=assignee_name,
                due_date=task.due_date,
                is_overdue=_is_task_overdue(task),
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
        finally:
            db.close()

    @strawberry.field
    def task_completion_stats(
        self, task_list_id: int, info: Info
    ) -> Optional[CompletionStats]:
        """Get completion stats for a task list - user must own it"""
        user = require_auth(info)
        db = get_db()
        try:
            # Verify user owns the task list
            task_list = (
                db.query(TaskListModel)
                .filter(
                    TaskListModel.id == task_list_id, TaskListModel.owner_id == user.id
                )
                .first()
            )

            if not task_list:
                return None

            # Reuse REST stats logic
            stats = (
                db.query(
                    func.count(TaskModel.id).label("total"),
                    func.sum(
                        case(
                            (TaskModel.status == DomainTaskStatus.COMPLETED, 1), else_=0
                        )
                    ).label("completed"),
                )
                .filter(TaskModel.task_list_id == task_list_id)
                .first()
            )

            total_tasks = stats.total or 0
            completed_tasks = stats.completed or 0
            completion_percentage = (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            )

            return CompletionStats(
                task_list_id=task_list_id,
                completion_percentage=round(completion_percentage, 1),
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
            )
        finally:
            db.close()


@strawberry.type
class TaskMutation:
    @strawberry.mutation
    async def create_task(self, input: TaskCreateInput, info: Info) -> Optional[Task]:
        """Create task - user must own the task list"""
        user = require_auth(info)
        db = get_db()
        try:
            # Verify user owns the task list (reuse REST logic)
            task_list = (
                db.query(TaskListModel)
                .filter(
                    TaskListModel.id == input.task_list_id,
                    TaskListModel.owner_id == user.id,
                )
                .first()
            )
            if not task_list:
                raise Exception("Task list not found")

            status = input.status.value if input.status else DomainTaskStatus.PENDING
            priority = (
                input.priority.value if input.priority else DomainTaskPriority.MEDIUM
            )

            task = TaskModel(
                title=input.title,
                description=input.description,
                status=status,
                priority=priority,
                task_list_id=input.task_list_id,
                assigned_to=input.assigned_to,
                due_date=input.due_date,
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            # Get assignee name (reuse REST logic)
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
                    db.query(UserModel)
                    .filter(UserModel.id == created_task.assigned_to)
                    .first()
                )
                if assignee:
                    notification_service = NotificationService()
                    await notification_service.send_task_assignment_notification(
                        created_task, assignee
                    )

            return Task(
                id=created_task.id,
                title=created_task.title,
                description=created_task.description,
                status=TaskStatus(created_task.status),
                priority=TaskPriority(created_task.priority),
                task_list_id=created_task.task_list_id,
                assigned_to=created_task.assigned_to,
                assignee_name=assignee_name,
                due_date=created_task.due_date,
                is_overdue=_is_task_overdue(created_task),
                created_at=created_task.created_at,
                updated_at=created_task.updated_at,
            )
        finally:
            db.close()

    def _update_task_fields(self, task: TaskModel, input: TaskUpdateInput) -> None:
        """Update task fields based on input"""
        if input.title is not None:
            task.title = input.title
        if input.description is not None:
            task.description = input.description
        if input.status is not None:
            task.status = input.status.value
        if input.priority is not None:
            task.priority = input.priority.value
        if input.assigned_to is not None:
            task.assigned_to = input.assigned_to
        if input.due_date is not None:
            task.due_date = input.due_date

    async def _send_completion_notification_if_needed(
        self, db, task: TaskModel, old_status: str
    ) -> None:
        """Send notification if task was just completed"""
        if (
            old_status != DomainTaskStatus.COMPLETED
            and task.status == DomainTaskStatus.COMPLETED
        ):
            task_list = (
                db.query(TaskListModel)
                .filter(TaskListModel.id == task.task_list_id)
                .first()
            )
            if task_list:
                owner = (
                    db.query(UserModel)
                    .filter(UserModel.id == task_list.owner_id)
                    .first()
                )
                if owner:
                    notification_service = NotificationService()
                    await notification_service.send_task_completion_notification(
                        task, owner
                    )

    def _get_task_with_assignee_name(self, db, task_id: int):
        """Get task with assignee name"""
        result = (
            db.query(TaskModel, UserModel.full_name.label("assignee_name"))
            .outerjoin(UserModel, TaskModel.assigned_to == UserModel.id)
            .filter(TaskModel.id == task_id)
            .first()
        )
        return result if result else (None, None)

    @strawberry.mutation
    async def update_task(
        self, id: int, input: TaskUpdateInput, info: Info
    ) -> Optional[Task]:
        """Update task - user must own the task list"""
        user = require_auth(info)
        db = get_db()
        try:
            task = (
                db.query(TaskModel)
                .join(TaskListModel)
                .filter(TaskModel.id == id, TaskListModel.owner_id == user.id)
                .first()
            )
            if not task:
                return None

            # Capture old status for notification logic
            old_status = task.status

            # Update fields
            self._update_task_fields(task, input)

            db.commit()
            db.refresh(task)

            # Send completion notification if needed
            await self._send_completion_notification_if_needed(db, task, old_status)

            # Get assignee name
            updated_task, assignee_name = self._get_task_with_assignee_name(db, task.id)
            if not updated_task:
                updated_task = task

            return Task(
                id=updated_task.id,
                title=updated_task.title,
                description=updated_task.description,
                status=TaskStatus(updated_task.status),
                priority=TaskPriority(updated_task.priority),
                task_list_id=updated_task.task_list_id,
                assigned_to=updated_task.assigned_to,
                assignee_name=assignee_name,
                due_date=updated_task.due_date,
                is_overdue=_is_task_overdue(updated_task),
                created_at=updated_task.created_at,
                updated_at=updated_task.updated_at,
            )
        finally:
            db.close()

    @strawberry.mutation
    def delete_task(self, id: int, info: Info) -> bool:
        """Delete task - user must own the task list"""
        user = require_auth(info)
        db = get_db()
        try:
            task = (
                db.query(TaskModel)
                .join(TaskListModel)
                .filter(TaskModel.id == id, TaskListModel.owner_id == user.id)
                .first()
            )
            if not task:
                return False

            db.delete(task)
            db.commit()
            return True
        finally:
            db.close()
