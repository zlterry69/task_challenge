import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest
from fastapi import HTTPException

from src.application.dto import TaskCreateDTO, TaskStatusUpdateDTO, TaskUpdateDTO
from src.domain.entities import TaskPriority, TaskStatus
from src.infrastructure.database import TaskListModel, TaskModel, UserModel
from src.presentation.routers import tasks


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    return MagicMock(id=1)


def test_get_task_completion_stats(mock_db, mock_user):
    # Crear un mock que devuelva valores enteros reales
    class MockStats:
        def __init__(self):
            self._total = 5
            self._completed = 2
            self._pending = 1
            self._in_progress = 1
            self._cancelled = 1

        @property
        def total(self):
            return self._total

        @property
        def completed(self):
            return self._completed

        @property
        def pending(self):
            return self._pending

        @property
        def in_progress(self):
            return self._in_progress

        @property
        def cancelled(self):
            return self._cancelled

    mock_stats = MockStats()
    mock_query = MagicMock()
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.with_entities.return_value = mock_query
    mock_query.first.return_value = mock_stats
    mock_db.query.return_value = mock_query

    result = tasks.get_task_completion_stats(db=mock_db, user=mock_user)
    assert result.total_tasks == 5
    assert result.completed_tasks == 2
    assert isinstance(result.completion_percentage, float)


def test_get_tasks(mock_db, mock_user):
    # Crear un mock que devuelva una tupla válida
    mock_task = create_autospec(TaskModel)
    mock_task.id = 1
    mock_task.title = "Task X"
    mock_task.description = "Test description"
    mock_task.status = TaskStatus.PENDING
    mock_task.priority = TaskPriority.MEDIUM
    mock_task.due_date = None
    mock_task.assigned_to = None
    mock_task.created_at = datetime.now()
    mock_task.updated_at = datetime.now()
    mock_task.task_list_id = 1

    # Configurar la cadena de mocks
    mock_query = MagicMock()
    mock_query.join.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [(mock_task, "John")]
    mock_db.query.return_value = mock_query

    result = tasks.get_tasks(db=mock_db, user=mock_user)
    assert len(result) == 1
    assert result[0].title == "Task X"


@pytest.mark.asyncio
async def test_create_task_success(monkeypatch, mock_db, mock_user):
    task_in = TaskCreateDTO(title="Task 1", task_list_id=1)

    # Crear mocks que devuelvan objetos válidos
    mock_tasklist = create_autospec(TaskListModel)
    mock_tasklist.id = 1
    mock_tasklist.owner_id = mock_user.id

    mock_task = create_autospec(TaskModel)
    mock_task.id = 10
    mock_task.title = "Task 1"
    mock_task.description = "Test description"
    mock_task.status = TaskStatus.PENDING
    mock_task.priority = TaskPriority.MEDIUM
    mock_task.due_date = None
    mock_task.assigned_to = None
    mock_task.created_at = datetime.now()
    mock_task.updated_at = datetime.now()
    mock_task.task_list_id = 1

    # Configurar la cadena de mocks para la primera consulta
    mock_query1 = MagicMock()
    mock_query1.filter.return_value = mock_query1
    mock_query1.first.return_value = mock_tasklist

    # Configurar la cadena de mocks para la segunda consulta
    mock_query2 = MagicMock()
    mock_query2.outerjoin.return_value = mock_query2
    mock_query2.filter.return_value = mock_query2
    mock_query2.first.return_value = (mock_task, "Assignee")

    # Configurar el mock_db para devolver diferentes queries
    mock_db.query.side_effect = [mock_query1, mock_query2]
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    # Mock NotificationService
    mock_notification_service = MagicMock()
    mock_notification_service.send_task_assignment_notification = AsyncMock()
    monkeypatch.setattr(
        tasks, "NotificationService", MagicMock(return_value=mock_notification_service)
    )

    result = await tasks.create_task(task_in, mock_db, mock_user)
    assert result.title == "Task 1"


def test_create_task_not_found(mock_db, mock_user):
    task_in = TaskCreateDTO(title="Task 1", task_list_id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        asyncio.run(tasks.create_task(task_in, mock_db, mock_user))
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_task_status_success(monkeypatch, mock_db, mock_user):
    # Crear mocks que devuelvan objetos válidos
    mock_task = create_autospec(TaskModel)
    mock_task.id = 1
    mock_task.status = TaskStatus.PENDING
    mock_task.task_list_id = 1
    mock_task.title = "Test Task"
    mock_task.description = "Test description"
    mock_task.priority = TaskPriority.MEDIUM
    mock_task.due_date = None
    mock_task.assigned_to = None
    mock_task.created_at = datetime.now()
    mock_task.updated_at = datetime.now()

    mock_tasklist = create_autospec(TaskListModel)
    mock_tasklist.id = 1
    mock_tasklist.owner_id = mock_user.id

    mock_user_obj = create_autospec(UserModel)
    mock_user_obj.id = 1

    # Configurar la cadena de mocks para la primera consulta
    mock_query1 = MagicMock()
    mock_query1.join.return_value = mock_query1
    mock_query1.filter.return_value = mock_query1
    mock_query1.first.return_value = mock_task

    # Configurar la cadena de mocks para las consultas adicionales
    mock_query2 = MagicMock()
    mock_query2.filter.return_value = mock_query2
    mock_query2.first.side_effect = [mock_tasklist, mock_user_obj]

    # Configurar la cadena de mocks para la consulta final
    mock_query3 = MagicMock()
    mock_query3.outerjoin.return_value = mock_query3
    mock_query3.filter.return_value = mock_query3
    mock_query3.first.return_value = (mock_task, "Assignee")

    # Configurar el mock_db para devolver diferentes queries
    mock_db.query.side_effect = [mock_query1, mock_query2, mock_query2, mock_query3]

    # Mock NotificationService
    mock_notification_service = MagicMock()
    mock_notification_service.send_task_completion_notification = AsyncMock()
    monkeypatch.setattr(
        tasks, "NotificationService", MagicMock(return_value=mock_notification_service)
    )

    status_update = TaskStatusUpdateDTO(status=TaskStatus.COMPLETED)
    result = await tasks.update_task_status(1, status_update, mock_db, mock_user)
    assert result.status == TaskStatus.COMPLETED


def test_update_task_status_not_found(mock_db, mock_user):
    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = (
        None
    )
    status_update = TaskStatusUpdateDTO(status=TaskStatus.COMPLETED)

    with pytest.raises(HTTPException):
        asyncio.run(tasks.update_task_status(1, status_update, mock_db, mock_user))


def test_delete_task_success(mock_db, mock_user):
    mock_task = MagicMock(title="Task X")
    mock_task.title = "Task X"
    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = (
        mock_task
    )

    result = tasks.delete_task(1, db=mock_db, user=mock_user)
    assert "deleted successfully" in result["message"]


def test_delete_task_not_found(mock_db, mock_user):
    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = (
        None
    )

    with pytest.raises(HTTPException):
        tasks.delete_task(1, db=mock_db, user=mock_user)


def test_update_task_success(mock_db, mock_user):
    mock_task = MagicMock(id=1, title="Old Task")
    mock_task.id = 1
    mock_task.title = "Old Task"
    mock_task.description = "Old description"
    mock_task.status = TaskStatus.PENDING
    mock_task.priority = TaskPriority.MEDIUM
    mock_task.due_date = None
    mock_task.assigned_to = None
    mock_task.created_at = datetime.now()
    mock_task.updated_at = datetime.now()
    mock_task.task_list_id = 1

    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = (
        mock_task
    )
    mock_db.query.return_value.outerjoin.return_value.filter.return_value.first.return_value = (
        mock_task,
        "John",
    )

    dto = TaskUpdateDTO(title="Updated Task")
    result = tasks.update_task(1, dto, db=mock_db, user=mock_user)
    assert result.title == "Updated Task"


def test_update_task_not_found(mock_db, mock_user):
    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = (
        None
    )

    with pytest.raises(HTTPException):
        tasks.update_task(1, TaskUpdateDTO(title="X"), db=mock_db, user=mock_user)
