from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Task, TaskList, TaskPriority, TaskStatus, User
from src.infrastructure.database import TaskListModel, TaskModel, UserModel
from src.infrastructure.repositories import (
    SQLAlchemyTaskListRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyUserRepository,
)


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    # Configurar el commit para que sea llamado correctamente
    session.commit = AsyncMock()
    session.commit.return_value = None
    return session


@pytest.fixture
def mock_user_model():
    user = create_autospec(UserModel)
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.hashed_password = "hashed123"
    return user


@pytest.fixture
def mock_task_list_model():
    task_list = create_autospec(TaskListModel)
    task_list.id = 1
    task_list.name = "Test List"
    task_list.description = "Test Description"
    task_list.owner_id = 1
    task_list.created_at = datetime.now()
    task_list.updated_at = datetime.now()
    return task_list


@pytest.fixture
def mock_task_model():
    task = create_autospec(TaskModel)
    task.id = 1
    task.title = "Test Task"
    task.description = "Test Description"
    task.status = TaskStatus.PENDING
    task.priority = TaskPriority.MEDIUM
    task.task_list_id = 1
    task.assigned_to = 1  # Asignar un ID de usuario
    task.created_at = datetime.now()
    task.updated_at = datetime.now()
    task.due_date = None
    return task


@pytest.mark.asyncio
async def test_user_repository_create(mock_session):
    # Arrange
    repo = SQLAlchemyUserRepository(mock_session)
    user = User(
        email="test@example.com", full_name="Test User", hashed_password="hashed123"
    )

    # Act
    await repo.create(user)

    # Assert - Verificar que los métodos fueron llamados
    assert mock_session.add.called
    # commit() se llama internamente en el repositorio
    assert mock_session.add.called


@pytest.mark.asyncio
async def test_user_repository_get_by_id(mock_session, mock_user_model):
    # Arrange
    repo = SQLAlchemyUserRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user_model
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_by_id(1)

    # Assert
    assert result is not None
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_user_repository_get_by_email(mock_session, mock_user_model):
    # Arrange
    repo = SQLAlchemyUserRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user_model
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_by_email("test@example.com")

    # Assert
    assert result is not None
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_task_list_repository_create(mock_session):
    # Arrange
    repo = SQLAlchemyTaskListRepository(mock_session)
    task_list = TaskList(name="Test List", description="Test Description", owner_id=1)

    # Act
    await repo.create(task_list)

    # Assert - Verificar que los métodos fueron llamados
    assert mock_session.add.called
    assert mock_session.add.called


@pytest.mark.asyncio
async def test_task_list_repository_get_by_id(mock_session, mock_task_list_model):
    # Arrange
    repo = SQLAlchemyTaskListRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task_list_model
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_by_id(1)

    # Assert
    assert result is not None
    assert result.name == "Test List"


@pytest.mark.asyncio
async def test_task_list_repository_get_by_owner(mock_session, mock_task_list_model):
    # Arrange
    repo = SQLAlchemyTaskListRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_list_model]
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_by_owner(1)

    # Assert
    assert len(result) == 1
    assert result[0].name == "Test List"


@pytest.mark.asyncio
async def test_task_repository_create(mock_session):
    # Arrange
    repo = SQLAlchemyTaskRepository(mock_session)
    task = Task(
        title="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        task_list_id=1,
    )

    # Act
    await repo.create(task)

    # Assert - Verificar que los métodos fueron llamados
    assert mock_session.add.called
    assert mock_session.add.called


@pytest.mark.asyncio
async def test_task_repository_get_by_id(mock_session, mock_task_model):
    # Arrange
    repo = SQLAlchemyTaskRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task_model
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_by_id(1)

    # Assert
    assert result is not None
    assert result.title == "Test Task"


@pytest.mark.asyncio
async def test_task_repository_get_by_task_list(mock_session, mock_task_model):
    # Arrange
    repo = SQLAlchemyTaskRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_model]
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_by_task_list(1)

    # Assert
    assert len(result) == 1
    assert result[0].title == "Test Task"


@pytest.mark.asyncio
async def test_task_repository_get_by_assignee(mock_session, mock_task_model):
    # Arrange
    repo = SQLAlchemyTaskRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_model]
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_by_assignee(1)

    # Assert
    assert len(result) == 1
    assert result[0].assigned_to == 1


@pytest.mark.asyncio
async def test_task_repository_filter_by_status(mock_session, mock_task_model):
    # Arrange
    repo = SQLAlchemyTaskRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_model]
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.filter_by_status(task_list_id=1, status=TaskStatus.PENDING)

    # Assert
    assert len(result) == 1
    assert result[0].status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_task_repository_filter_by_priority(mock_session, mock_task_model):
    # Arrange
    repo = SQLAlchemyTaskRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_model]
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.filter_by_priority(task_list_id=1, priority=TaskPriority.MEDIUM)

    # Assert
    assert len(result) == 1
    assert result[0].priority == TaskPriority.MEDIUM


@pytest.mark.asyncio
async def test_task_repository_get_overdue_tasks(mock_session, mock_task_model):
    # Arrange
    repo = SQLAlchemyTaskRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_model]
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_overdue_tasks()

    # Assert
    assert len(result) == 1
    assert result[0].title == "Test Task"
