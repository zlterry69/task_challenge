from typing import List, Optional

import strawberry
from sqlalchemy import case, func
from strawberry.types import Info

from src.domain.entities import TaskStatus
from src.infrastructure.database import TaskListModel, TaskModel

from ..context import get_db, require_auth
from ..types import TaskList, TaskListCreateInput, TaskListUpdateInput


@strawberry.type
class TaskListQuery:
    @strawberry.field
    def task_lists(self, info: Info) -> List[TaskList]:
        """Get all task lists for authenticated user with completion stats"""
        user = require_auth(info)
        db = get_db()
        try:
            # Reuse REST logic for completion stats
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

            task_lists = []
            for task_list, total_tasks, completed_tasks in results:
                completion_percentage = 0.0
                if total_tasks and total_tasks > 0:
                    completed_tasks = completed_tasks or 0
                    completion_percentage = (completed_tasks / total_tasks) * 100

                task_lists.append(
                    TaskList(
                        id=task_list.id,
                        name=task_list.name,
                        description=task_list.description,
                        owner_id=task_list.owner_id,
                        completion_percentage=round(completion_percentage, 1),
                        task_count=total_tasks or 0,
                        created_at=task_list.created_at,
                        updated_at=task_list.updated_at,
                    )
                )

            return task_lists
        finally:
            db.close()

    @strawberry.field
    def task_list(self, id: int, info: Info) -> Optional[TaskList]:
        """Get specific task list with completion stats - user must own it"""
        user = require_auth(info)
        db = get_db()
        try:
            # Reuse REST logic for single task list
            result = (
                db.query(
                    TaskListModel,
                    func.count(TaskModel.id).label("total_tasks"),
                    func.sum(
                        case((TaskModel.status == TaskStatus.COMPLETED, 1), else_=0)
                    ).label("completed_tasks"),
                )
                .outerjoin(TaskModel, TaskListModel.id == TaskModel.task_list_id)
                .filter(TaskListModel.id == id, TaskListModel.owner_id == user.id)
                .group_by(TaskListModel.id)
                .first()
            )

            if not result:
                return None

            task_list, total_tasks, completed_tasks = result

            completion_percentage = 0.0
            if total_tasks and total_tasks > 0:
                completed_tasks = completed_tasks or 0
                completion_percentage = (completed_tasks / total_tasks) * 100

            return TaskList(
                id=task_list.id,
                name=task_list.name,
                description=task_list.description,
                owner_id=task_list.owner_id,
                completion_percentage=round(completion_percentage, 1),
                task_count=total_tasks or 0,
                created_at=task_list.created_at,
                updated_at=task_list.updated_at,
            )
        finally:
            db.close()


@strawberry.type
class TaskListMutation:
    @strawberry.mutation
    def create_task_list(self, input: TaskListCreateInput, info: Info) -> TaskList:
        """Create new task list for authenticated user"""
        user = require_auth(info)
        db = get_db()
        try:
            task_list = TaskListModel(
                name=input.name, description=input.description, owner_id=user.id
            )
            db.add(task_list)
            db.commit()
            db.refresh(task_list)

            return TaskList(
                id=task_list.id,
                name=task_list.name,
                description=task_list.description,
                owner_id=task_list.owner_id,
                completion_percentage=0.0,
                task_count=0,
                created_at=task_list.created_at,
                updated_at=task_list.updated_at,
            )
        finally:
            db.close()

    @strawberry.mutation
    def update_task_list(
        self, id: int, input: TaskListUpdateInput, info: Info
    ) -> Optional[TaskList]:
        """Update task list - user must own it"""
        user = require_auth(info)
        db = get_db()
        try:
            task_list = (
                db.query(TaskListModel)
                .filter(TaskListModel.id == id, TaskListModel.owner_id == user.id)
                .first()
            )
            if not task_list:
                return None

            if input.name is not None:
                task_list.name = input.name
            if input.description is not None:
                task_list.description = input.description

            db.commit()
            db.refresh(task_list)

            # Get updated stats (reuse REST logic)
            result = (
                db.query(
                    TaskListModel,
                    func.count(TaskModel.id).label("total_tasks"),
                    func.sum(
                        case((TaskModel.status == TaskStatus.COMPLETED, 1), else_=0)
                    ).label("completed_tasks"),
                )
                .outerjoin(TaskModel, TaskListModel.id == TaskModel.task_list_id)
                .filter(TaskListModel.id == id, TaskListModel.owner_id == user.id)
                .group_by(TaskListModel.id)
                .first()
            )

            updated_task_list, total_tasks, completed_tasks = (
                result if result else (task_list, 0, 0)
            )

            completion_percentage = 0.0
            if total_tasks and total_tasks > 0:
                completed_tasks = completed_tasks or 0
                completion_percentage = (completed_tasks / total_tasks) * 100

            return TaskList(
                id=updated_task_list.id,
                name=updated_task_list.name,
                description=updated_task_list.description,
                owner_id=updated_task_list.owner_id,
                completion_percentage=round(completion_percentage, 1),
                task_count=total_tasks or 0,
                created_at=updated_task_list.created_at,
                updated_at=updated_task_list.updated_at,
            )
        finally:
            db.close()

    @strawberry.mutation
    def delete_task_list(self, id: int, info: Info) -> bool:
        """Delete task list - user must own it"""
        user = require_auth(info)
        db = get_db()
        try:
            task_list = (
                db.query(TaskListModel)
                .filter(TaskListModel.id == id, TaskListModel.owner_id == user.id)
                .first()
            )
            if not task_list:
                return False

            db.delete(task_list)
            db.commit()
            return True
        finally:
            db.close()
