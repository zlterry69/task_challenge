from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from src.domain.entities import TaskStatus
from src.domain.exceptions import (
    EntityNotFoundError,
    TaskAssignmentError,
    TaskListOwnershipError,
    TaskStatusError,
    UnauthorizedError,
)
from src.infrastructure.database import TaskListModel, TaskModel, UserModel

from .dto import CompletionStatsDTO, TaskCreateDTO, TaskFilterDTO, TaskListCreateDTO


class TaskListService:
    def __init__(self, db: Session):
        self.db = db

    def create_task_list(
        self, task_list_dto: TaskListCreateDTO, owner_id: int
    ) -> TaskListModel:
        # Verify owner exists
        owner = self.db.query(UserModel).filter(UserModel.id == owner_id).first()
        if not owner:
            raise EntityNotFoundError("User", str(owner_id))

        task_list = TaskListModel(
            name=task_list_dto.name,
            description=task_list_dto.description,
            owner_id=owner_id,
            created_at=datetime.utcnow(),
        )

        self.db.add(task_list)
        self.db.commit()
        self.db.refresh(task_list)
        return task_list

    def get_task_list_with_stats(
        self, task_list_id: int, user_id: int
    ) -> TaskListModel:
        task_list = (
            self.db.query(TaskListModel)
            .filter(TaskListModel.id == task_list_id)
            .first()
        )
        if not task_list:
            raise EntityNotFoundError("TaskList", str(task_list_id))

        # Check ownership (basic business rule)
        if task_list.owner_id != user_id:
            raise TaskListOwnershipError()

        return task_list

    def calculate_completion_stats(self, task_list_id: int) -> CompletionStatsDTO:
        tasks = (
            self.db.query(TaskModel)
            .filter(TaskModel.task_list_id == task_list_id)
            .all()
        )

        total_tasks = len(tasks)
        completed_tasks = sum(
            1 for task in tasks if task.status == TaskStatus.COMPLETED
        )
        pending_tasks = sum(1 for task in tasks if task.status == TaskStatus.PENDING)
        in_progress_tasks = sum(
            1 for task in tasks if task.status == TaskStatus.IN_PROGRESS
        )
        cancelled_tasks = sum(
            1 for task in tasks if task.status == TaskStatus.CANCELLED
        )

        completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        )

        return CompletionStatsDTO(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            cancelled_tasks=cancelled_tasks,
            completion_percentage=completion_percentage,
        )


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_dto: TaskCreateDTO, user_id: int) -> TaskModel:
        # Verify task list exists and user owns it
        task_list = (
            self.db.query(TaskListModel)
            .filter(TaskListModel.id == task_dto.task_list_id)
            .first()
        )
        if not task_list:
            raise EntityNotFoundError("TaskList", str(task_dto.task_list_id))

        if task_list.owner_id != user_id:
            raise TaskListOwnershipError()

        # Verify assignee exists if provided
        if task_dto.assigned_to:
            assignee = (
                self.db.query(UserModel)
                .filter(UserModel.id == task_dto.assigned_to)
                .first()
            )
            if not assignee:
                raise EntityNotFoundError("User", str(task_dto.assigned_to))
            if not assignee.is_active:
                raise TaskAssignmentError("Cannot assign task to inactive user")

        task = TaskModel(
            title=task_dto.title,
            description=task_dto.description,
            priority=task_dto.priority,
            task_list_id=task_dto.task_list_id,
            assigned_to=task_dto.assigned_to,
            due_date=task_dto.due_date,
            created_at=datetime.utcnow(),
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task_status(
        self, task_id: int, new_status: TaskStatus, user_id: int
    ) -> TaskModel:
        task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise EntityNotFoundError("Task", str(task_id))

        # Check ownership through task list
        task_list = (
            self.db.query(TaskListModel)
            .filter(TaskListModel.id == task.task_list_id)
            .first()
        )
        if task_list.owner_id != user_id and task.assigned_to != user_id:
            raise UnauthorizedError("Cannot update task status")

        # Business rules for status transitions
        current_status = task.status
        if not self._is_valid_status_transition(current_status, new_status):
            raise TaskStatusError(
                f"Cannot transition from {current_status} to {new_status}"
            )

        task.status = new_status
        task.updated_at = datetime.utcnow()

        # If completing the task, set completion timestamp
        if new_status == TaskStatus.COMPLETED:
            task.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(task)
        return task

    def assign_task(self, task_id: int, assignee_id: int, user_id: int) -> TaskModel:
        task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise EntityNotFoundError("Task", str(task_id))

        # Check ownership
        task_list = (
            self.db.query(TaskListModel)
            .filter(TaskListModel.id == task.task_list_id)
            .first()
        )
        if task_list.owner_id != user_id:
            raise TaskListOwnershipError()

        # Verify assignee exists and is active
        assignee = self.db.query(UserModel).filter(UserModel.id == assignee_id).first()
        if not assignee:
            raise EntityNotFoundError("User", str(assignee_id))
        if not assignee.is_active:
            raise TaskAssignmentError("Cannot assign task to inactive user")

        # Business rule: Cannot assign completed or cancelled tasks
        if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            raise TaskAssignmentError(f"Cannot assign {task.status} task")

        task.assigned_to = assignee_id
        task.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(task)
        return task

    def get_filtered_tasks(
        self, filter_dto: TaskFilterDTO, user_id: int
    ) -> List[TaskModel]:
        query = self.db.query(TaskModel)

        # Join with task list for ownership check
        query = query.join(TaskListModel)

        # Filter by user access (owns task list or is assigned to task)
        query = query.filter(
            (TaskListModel.owner_id == user_id) | (TaskModel.assigned_to == user_id)
        )

        # Apply filters
        if filter_dto.task_list_id:
            query = query.filter(TaskModel.task_list_id == filter_dto.task_list_id)

        if filter_dto.status:
            query = query.filter(TaskModel.status == filter_dto.status)

        if filter_dto.priority:
            query = query.filter(TaskModel.priority == filter_dto.priority)

        if filter_dto.assigned_to:
            query = query.filter(TaskModel.assigned_to == filter_dto.assigned_to)

        if filter_dto.overdue_only:
            query = query.filter(
                TaskModel.due_date < datetime.utcnow(),
                TaskModel.status != TaskStatus.COMPLETED,
            )

        return query.all()

    def get_overdue_tasks(self, user_id: int) -> List[TaskModel]:
        return (
            self.db.query(TaskModel)
            .join(TaskListModel)
            .filter(
                (TaskListModel.owner_id == user_id)
                | (TaskModel.assigned_to == user_id),
                TaskModel.due_date < datetime.utcnow(),
                TaskModel.status != TaskStatus.COMPLETED,
            )
            .all()
        )

    def _is_valid_status_transition(self, current: TaskStatus, new: TaskStatus) -> bool:
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.IN_PROGRESS: [
                TaskStatus.COMPLETED,
                TaskStatus.PENDING,
                TaskStatus.CANCELLED,
            ],
            TaskStatus.COMPLETED: [],  # Cannot transition from completed
            TaskStatus.CANCELLED: [TaskStatus.PENDING],  # Can reopen cancelled tasks
        }

        return new in valid_transitions.get(current, [])


class NotificationService:
    def __init__(self):
        self.enabled = True

    async def send_task_assignment_notification(
        self, task: TaskModel, assignee: UserModel
    ) -> bool:
        if not self.enabled:
            return False

        # Simulate email sending
        print(f"📧 FICTITIOUS EMAIL: Task '{task.title}' assigned to {assignee.email}")
        return True

    async def send_task_completion_notification(
        self, task: TaskModel, owner: UserModel
    ) -> bool:
        if not self.enabled:
            return False

        # Simulate email sending
        print(
            f"📧 FICTITIOUS EMAIL: Task '{task.title}' completed! Notification sent to {owner.email}"
        )
        return True

    async def send_overdue_task_notification(
        self, tasks: List[TaskModel], user: UserModel
    ) -> bool:
        if not self.enabled or not tasks:
            return False

        task_count = len(tasks)
        print(
            f"📧 FICTITIOUS EMAIL: You have {task_count} overdue task(s). Notification sent to {user.email}"
        )
        return True
