from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.entities import TaskPriority, TaskStatus
from src.presentation.graphql.context import get_db, require_auth
from src.presentation.graphql.resolvers.task_list_resolvers import (
    TaskListMutation,
    TaskListQuery,
)
from src.presentation.graphql.resolvers.task_resolvers import TaskMutation, TaskQuery
from src.presentation.graphql.types import (
    TaskCreateInput,
    TaskListCreateInput,
    TaskListUpdateInput,
    TaskStatusUpdateInput,
    TaskUpdateInput,
)


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_info(mock_db, mock_user):
    info = MagicMock()
    info.context = {"db": mock_db, "user": mock_user}
    return info


# Tests para TaskQuery
@pytest.mark.asyncio
async def test_task_query_tasks_execution(mock_info):
    """Test que ejecuta realmente el método tasks"""
    query = TaskQuery()

    # Mock de la respuesta de la base de datos
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_info.context["db"].execute.return_value = mock_result

    result = await query.tasks(info=mock_info)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_task_query_task_execution(mock_info):
    """Test que ejecuta realmente el método task"""
    query = TaskQuery()

    # Mock de la respuesta de la base de datos
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_info.context["db"].execute.return_value = mock_result

    result = await query.task(id=1, info=mock_info)
    assert result is None


# Tests para TaskMutation
@pytest.mark.asyncio
async def test_task_mutation_create_task_execution(mock_info):
    """Test que ejecuta realmente el método create_task"""
    mutation = TaskMutation()
    input_data = TaskCreateInput(
        title="New Task",
        description="New Description",
        task_list_id=1,
        priority=TaskPriority.MEDIUM,
    )

    # Mock de la respuesta de la base de datos
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "New Task"
    mock_task.description = "New Description"
    mock_task.status = TaskStatus.PENDING
    mock_task.priority = TaskPriority.MEDIUM
    mock_task.task_list_id = 1
    mock_task.created_at = datetime.now()
    mock_task.updated_at = datetime.now()

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = mock_task
    mock_info.context["db"].execute.return_value = mock_result

    with patch("src.presentation.graphql.resolvers.task_resolvers.NotificationService"):
        result = await mutation.create_task(input=input_data, info=mock_info)
        assert result.title == "New Task"


@pytest.mark.asyncio
async def test_task_mutation_update_task_execution(mock_info):
    """Test que ejecuta realmente el método update_task"""
    mutation = TaskMutation()
    input_data = TaskUpdateInput(title="Updated Task", priority=TaskPriority.HIGH)

    # Mock de la respuesta de la base de datos
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "Updated Task"
    mock_task.priority = TaskPriority.HIGH

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_info.context["db"].execute.return_value = mock_result

    result = await mutation.update_task(id=1, input=input_data, info=mock_info)
    assert result.title == "Updated Task"


@pytest.mark.asyncio
async def test_task_mutation_delete_task_execution(mock_info):
    """Test que ejecuta realmente el método delete_task"""
    mutation = TaskMutation()

    # Mock de la respuesta de la base de datos
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.task_list_id = 1

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_info.context["db"].execute.return_value = mock_result

    result = await mutation.delete_task(id=1, info=mock_info)
    assert result is True


@pytest.mark.asyncio
async def test_task_mutation_update_task_status_execution(mock_info):
    """Test que ejecuta realmente el método update_task_status"""
    mutation = TaskMutation()
    input_data = TaskStatusUpdateInput(status=TaskStatus.COMPLETED)

    # Mock de la respuesta de la base de datos
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.status = TaskStatus.COMPLETED
    mock_task.task_list_id = 1

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_info.context["db"].execute.return_value = mock_result

    with patch("src.presentation.graphql.resolvers.task_resolvers.NotificationService"):
        result = await mutation.update_task_status(
            id=1, input=input_data, info=mock_info
        )
        assert result.status == TaskStatus.COMPLETED


# Tests para TaskListQuery
@pytest.mark.asyncio
async def test_task_list_query_task_lists_execution(mock_info):
    """Test que ejecuta realmente el método task_lists"""
    query = TaskListQuery()

    # Mock de la respuesta de la base de datos
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_info.context["db"].execute.return_value = mock_result

    result = await query.task_lists(info=mock_info)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_task_list_query_task_list_execution(mock_info):
    """Test que ejecuta realmente el método task_list"""
    query = TaskListQuery()

    # Mock de la respuesta de la base de datos
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_info.context["db"].execute.return_value = mock_result

    result = await query.task_list(id=1, info=mock_info)
    assert result is None


# Tests para TaskListMutation
@pytest.mark.asyncio
async def test_task_list_mutation_create_task_list_execution(mock_info):
    """Test que ejecuta realmente el método create_task_list"""
    mutation = TaskListMutation()
    input_data = TaskListCreateInput(name="New List", description="New Description")

    # Mock de la respuesta de la base de datos
    mock_task_list = MagicMock()
    mock_task_list.id = 1
    mock_task_list.name = "New List"
    mock_task_list.description = "New Description"
    mock_task_list.owner_id = 1

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = mock_task_list
    mock_info.context["db"].execute.return_value = mock_result

    result = await mutation.create_task_list(input=input_data, info=mock_info)
    assert result.name == "New List"


@pytest.mark.asyncio
async def test_task_list_mutation_update_task_list_execution(mock_info):
    """Test que ejecuta realmente el método update_task_list"""
    mutation = TaskListMutation()
    input_data = TaskListUpdateInput(
        name="Updated List", description="Updated Description"
    )

    # Mock de la respuesta de la base de datos
    mock_task_list = MagicMock()
    mock_task_list.id = 1
    mock_task_list.name = "Updated List"
    mock_task_list.description = "Updated Description"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task_list
    mock_info.context["db"].execute.return_value = mock_result

    result = await mutation.update_task_list(id=1, input=input_data, info=mock_info)
    assert result.name == "Updated List"


@pytest.mark.asyncio
async def test_task_list_mutation_delete_task_list_execution(mock_info):
    """Test que ejecuta realmente el método delete_task_list"""
    mutation = TaskListMutation()

    # Mock de la respuesta de la base de datos
    mock_task_list = MagicMock()
    mock_task_list.id = 1
    mock_task_list.owner_id = 1

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task_list
    mock_info.context["db"].execute.return_value = mock_result

    result = await mutation.delete_task_list(id=1, info=mock_info)
    assert result is True


# Test para get_db y require_auth
def test_get_db_function():
    """Test que ejecuta la función get_db"""
    with patch("src.presentation.graphql.context.SessionLocal") as mock_session:
        mock_db_instance = MagicMock()
        mock_session.return_value = mock_db_instance

        result = get_db()
        assert result == mock_db_instance


def test_require_auth_function():
    """Test que ejecuta la función require_auth"""
    mock_info = MagicMock()
    mock_user = MagicMock()
    mock_info.context = {"user": mock_user}

    result = require_auth(mock_info)
    assert result == mock_user


def test_require_auth_no_user():
    """Test que ejecuta require_auth sin usuario"""
    mock_info = MagicMock()
    mock_info.context = {}

    with pytest.raises(Exception, match="Authentication required"):
        require_auth(mock_info)
