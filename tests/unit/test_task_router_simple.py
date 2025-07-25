from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest

from src.application.dto import TaskCreateDTO, TaskStatusUpdateDTO
from src.domain.entities import TaskPriority, TaskStatus
from src.infrastructure.database import TaskListModel, TaskModel, UserModel
from src.presentation.routers import tasks


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


@pytest.fixture
def mock_db():
    db = MagicMock()
    # Configurar cadenas específicas de mocks para diferentes queries
    query_chain = MagicMock()
    query_chain.join.return_value = query_chain
    query_chain.outerjoin.return_value = query_chain
    query_chain.filter.return_value = query_chain
    query_chain.with_entities.return_value = query_chain

    db.query.return_value = query_chain
    return db


@pytest.fixture
def mock_user():
    return MagicMock(id=1)


@pytest.fixture
def mock_task_model():
    task = create_autospec(TaskModel)
    task.id = 1
    task.title = "Test Task"
    task.description = "Test Description"
    task.status = TaskStatus.PENDING
    task.priority = TaskPriority.MEDIUM
    task.task_list_id = 1
    task.created_at = datetime.now()
    task.updated_at = datetime.now()
    task.assigned_to = None
    task.due_date = None
    return task


def test_get_task_completion_stats_simple(mock_db, mock_user):
    """Test simple para get_task_completion_stats"""
    # Mock que devuelva valores reales
    mock_stats = MockStats()
    mock_db.query.return_value.join.return_value.filter.return_value.with_entities.return_value.first.return_value = (
        mock_stats
    )

    result = tasks.get_task_completion_stats(db=mock_db, user=mock_user)
    assert result.total_tasks == 5
    assert result.completed_tasks == 2
    assert isinstance(result.completion_percentage, float)


def test_get_tasks_simple(mock_db, mock_user, mock_task_model):
    """Test simple para get_tasks"""
    # Configurar el mock para que devuelva una tupla con el task y el nombre del asignado
    mock_db.query.return_value.join.return_value.outerjoin.return_value.filter.return_value.all.return_value = [
        (mock_task_model, "John")
    ]

    result = tasks.get_tasks(db=mock_db, user=mock_user)
    assert len(result) == 1
    assert result[0].title == "Test Task"


@pytest.mark.asyncio
async def test_create_task_simple(monkeypatch, mock_db, mock_user, mock_task_model):
    """Test simple para create_task"""
    task_in = TaskCreateDTO(title="Task 1", task_list_id=1)

    # Mock que devuelva valores reales
    mock_tasklist = MagicMock()
    mock_tasklist.id = 1
    mock_tasklist.owner_id = mock_user.id

    # Configurar diferentes comportamientos para diferentes tipos de query
    def mock_query_side_effect(*args):
        if args[0] == TaskListModel:  # Query para verificar task list
            query_mock = MagicMock()
            query_mock.filter.return_value.first.return_value = mock_tasklist
            return query_mock
        else:  # Query para obtener el task con assignee
            query_mock = MagicMock()
            query_mock.outerjoin.return_value.filter.return_value.first.return_value = (
                mock_task_model,
                "Assignee",
            )
            return query_mock

    mock_db.query.side_effect = mock_query_side_effect

    # Mock NotificationService
    mock_notification_service = MagicMock()
    mock_notification_service.send_task_assignment_notification = AsyncMock()
    monkeypatch.setattr(
        tasks, "NotificationService", MagicMock(return_value=mock_notification_service)
    )

    result = await tasks.create_task(task_in, mock_db, mock_user)
    assert result.title == "Test Task"


@pytest.mark.asyncio
async def test_update_task_status_simple(
    monkeypatch, mock_db, mock_user, mock_task_model
):
    """Test simple para update_task_status"""
    # Mock que devuelva valores reales
    mock_tasklist = MagicMock()
    mock_tasklist.id = 1
    mock_tasklist.owner_id = mock_user.id

    mock_user_obj = MagicMock()
    mock_user_obj.id = 1

    # Configurar diferentes comportamientos para diferentes tipos de query
    def mock_query_side_effect(*args):
        if args[0] == TaskModel:  # Query para obtener el task con join
            query_mock = MagicMock()
            query_mock.join.return_value.filter.return_value.first.return_value = (
                mock_task_model
            )
            query_mock.outerjoin.return_value.filter.return_value.first.return_value = (
                mock_task_model,
                "Assignee",
            )
            return query_mock
        elif args[0] == TaskListModel:  # Query para task list
            query_mock = MagicMock()
            query_mock.filter.return_value.first.return_value = mock_tasklist
            return query_mock
        elif args[0] == UserModel:  # Query para user
            query_mock = MagicMock()
            query_mock.filter.return_value.first.return_value = mock_user_obj
            return query_mock

    mock_db.query.side_effect = mock_query_side_effect

    # Mock NotificationService
    mock_notification_service = MagicMock()
    mock_notification_service.send_task_completion_notification = AsyncMock()
    monkeypatch.setattr(
        tasks, "NotificationService", MagicMock(return_value=mock_notification_service)
    )

    status_update = TaskStatusUpdateDTO(status=TaskStatus.COMPLETED)
    result = await tasks.update_task_status(1, status_update, mock_db, mock_user)
    assert result.title == "Test Task"
