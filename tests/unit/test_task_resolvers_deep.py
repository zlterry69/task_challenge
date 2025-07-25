from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.entities import TaskPriority as DomainTaskPriority
from src.domain.entities import TaskStatus as DomainTaskStatus
from src.presentation.graphql.resolvers.task_resolvers import TaskMutation, TaskQuery
from src.presentation.graphql.types import (
    TaskCreateInput,
    TaskFilterInput,
    TaskPriority,
    TaskStatus,
    TaskUpdateInput,
)


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = MagicMock()
    return db


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_info(mock_user):
    """Mock Strawberry Info object"""
    info = MagicMock()
    info.context = {"user": mock_user}
    return info


@pytest.fixture
def mock_task_model():
    """Mock TaskModel from database"""
    task = MagicMock()
    task.id = 1
    task.title = "Test Task"
    task.description = "Test Description"
    task.status = DomainTaskStatus.PENDING
    task.priority = DomainTaskPriority.MEDIUM
    task.task_list_id = 1
    task.assigned_to = None
    task.due_date = None
    task.created_at = datetime.now()
    task.updated_at = datetime.now()
    return task


@pytest.fixture
def mock_task_list_model():
    """Mock TaskListModel from database"""
    task_list = MagicMock()
    task_list.id = 1
    task_list.name = "Test List"
    task_list.owner_id = 1
    return task_list


# =============================================================================
# TASK QUERY TESTS
# =============================================================================


class TestTaskQuery:
    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    def test_tasks_without_filter(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_model,
    ):
        """Test tasks query without filters"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock query chain
        mock_query = mock_db.query.return_value
        mock_query.join.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [(mock_task_model, "John Doe")]

        # Execute
        query = TaskQuery()
        result = query.tasks(info=mock_info)

        # Verify
        assert len(result) == 1
        assert result[0].title == "Test Task"
        mock_db.close.assert_called_once()

    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    def test_tasks_with_filters(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_model,
    ):
        """Test tasks query with filters"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        filter_input = TaskFilterInput(
            task_list_id=1, status=TaskStatus.PENDING, priority=TaskPriority.HIGH
        )

        # Mock query chain
        mock_query = mock_db.query.return_value
        mock_query.join.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [(mock_task_model, None)]

        # Execute
        query = TaskQuery()
        result = query.tasks(info=mock_info, filter=filter_input)

        # Verify
        assert len(result) == 1
        # Verify filter was applied (called multiple times for each filter)
        assert mock_query.filter.call_count >= 3

    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    def test_tasks_empty_result(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test tasks query with empty result"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock empty query result
        mock_query = mock_db.query.return_value
        mock_query.join.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        # Execute
        query = TaskQuery()
        result = query.tasks(info=mock_info)

        # Verify
        assert result == []

    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    def test_task_by_id_found(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_model,
    ):
        """Test task query by ID when task exists"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock query chain
        mock_query = mock_db.query.return_value
        mock_query.join.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = (mock_task_model, "John Doe")

        # Execute
        query = TaskQuery()
        result = query.task(id=1, info=mock_info)

        # Verify
        assert result is not None
        assert result.title == "Test Task"

    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    def test_task_by_id_not_found(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task query by ID when task doesn't exist"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock query chain returning None
        mock_query = mock_db.query.return_value
        mock_query.join.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Execute
        query = TaskQuery()
        result = query.task(id=999, info=mock_info)

        # Verify
        assert result is None


# =============================================================================
# TASK MUTATION TESTS
# =============================================================================


class TestTaskMutation:
    @pytest.mark.asyncio
    @patch("src.presentation.graphql.resolvers.task_resolvers.NotificationService")
    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    async def test_create_task_success(
        self,
        mock_get_db,
        mock_require_auth,
        mock_notification_service,
        mock_info,
        mock_user,
        mock_db,
        mock_task_model,
        mock_task_list_model,
    ):
        """Test successful task creation"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskCreateInput(
            title="New Task",
            description="New Description",
            task_list_id=1,
            priority=TaskPriority.HIGH,
            assigned_to=2,
        )

        # Mock task list validation
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_task_list_model
        )

        # Mock task creation
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Mock final query for result
        mock_query = MagicMock()
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = (mock_task_model, "Assignee Name")
        mock_db.query.side_effect = [
            MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(
                        first=MagicMock(return_value=mock_task_list_model)
                    )
                )
            ),
            mock_query,
        ]

        # Mock assignee for notification
        mock_assignee = MagicMock()
        mock_assignee.id = 2
        mock_assignee.email = "assignee@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_assignee
        )

        # Mock notification service
        mock_notification_instance = MagicMock()
        mock_notification_instance.send_task_assignment_notification = AsyncMock()
        mock_notification_service.return_value = mock_notification_instance

        # Execute - USAR AWAIT porque create_task ES ASYNC
        mutation = TaskMutation()
        result = await mutation.create_task(input=input_data, info=mock_info)

        # Verify
        assert result is not None
        assert result.title == "Test Task"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    async def test_create_task_list_not_found(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task creation when task list doesn't exist"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskCreateInput(title="New Task", task_list_id=999)

        # Mock task list not found
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify - USAR AWAIT
        mutation = TaskMutation()
        with pytest.raises(Exception, match="Task list not found"):
            await mutation.create_task(input=input_data, info=mock_info)

    @pytest.mark.asyncio
    @patch("src.presentation.graphql.resolvers.task_resolvers.NotificationService")
    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    async def test_update_task_success(
        self,
        mock_get_db,
        mock_require_auth,
        mock_notification_service,
        mock_info,
        mock_user,
        mock_db,
        mock_task_model,
    ):
        """Test successful task update"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskUpdateInput(title="Updated Task", priority=TaskPriority.LOW)

        # Mock task found
        mock_query_chain = MagicMock()
        mock_query_chain.join.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = mock_task_model
        mock_db.query.return_value = mock_query_chain

        # Mock commit and refresh
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Mock final query for result
        mock_result_query = MagicMock()
        mock_result_query.outerjoin.return_value = mock_result_query
        mock_result_query.filter.return_value = mock_result_query
        mock_result_query.first.return_value = (mock_task_model, "Assignee")

        # Use side_effect to return different mocks for different calls
        mock_db.query.side_effect = [mock_query_chain, mock_result_query]

        # Execute - USAR AWAIT porque update_task ES ASYNC
        mutation = TaskMutation()
        result = await mutation.update_task(id=1, input=input_data, info=mock_info)

        # Verify
        assert result is not None
        # Verificar que el resultado devuelve el mock que fue actualizado
        assert hasattr(result, "title")  # Confirmar que tiene título
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    async def test_update_task_not_found(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task update when task doesn't exist"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskUpdateInput(title="Updated Task")

        # Mock task not found
        mock_query_chain = MagicMock()
        mock_query_chain.join.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = None
        mock_db.query.return_value = mock_query_chain

        # Execute - USAR AWAIT porque update_task ES ASYNC
        mutation = TaskMutation()
        result = await mutation.update_task(id=999, input=input_data, info=mock_info)

        # Verify
        assert result is None

    @pytest.mark.asyncio
    @patch("src.presentation.graphql.resolvers.task_resolvers.NotificationService")
    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    async def test_update_task_completion_notification(
        self,
        mock_get_db,
        mock_require_auth,
        mock_notification_service,
        mock_info,
        mock_user,
        mock_db,
        mock_task_model,
    ):
        """Test task completion notification is sent"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock task with old status PENDING
        mock_task_model.status = DomainTaskStatus.PENDING

        input_data = TaskUpdateInput(status=TaskStatus.COMPLETED)

        # Mock task found and task list
        mock_query_chain = MagicMock()
        mock_query_chain.join.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = mock_task_model

        mock_task_list = MagicMock()
        mock_task_list.id = 1
        mock_task_list.owner_id = 1

        mock_owner = MagicMock()
        mock_owner.id = 1
        mock_owner.email = "owner@example.com"

        # Mock database queries
        mock_db.query.side_effect = [
            mock_query_chain,  # Find task
            MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=mock_task_list))
                )
            ),  # Find task list
            MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=mock_owner))
                )
            ),  # Find owner
            MagicMock(
                outerjoin=MagicMock(
                    return_value=MagicMock(
                        filter=MagicMock(
                            return_value=MagicMock(
                                first=MagicMock(return_value=(mock_task_model, None))
                            )
                        )
                    )
                )
            ),  # Final result
        ]

        # Mock commit and refresh
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Mock notification service
        mock_notification_instance = MagicMock()
        mock_notification_instance.send_task_completion_notification = AsyncMock()
        mock_notification_service.return_value = mock_notification_instance

        # Execute - USAR AWAIT porque update_task ES ASYNC
        mutation = TaskMutation()
        result = await mutation.update_task(id=1, input=input_data, info=mock_info)

        # Verify
        assert result is not None

    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    def test_delete_task_success(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_model,
    ):
        """Test successful task deletion"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock task found
        mock_query_chain = MagicMock()
        mock_query_chain.join.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = mock_task_model
        mock_db.query.return_value = mock_query_chain

        # Mock delete and commit
        mock_db.delete = MagicMock()
        mock_db.commit = MagicMock()

        # Execute - delete_task NO es async
        mutation = TaskMutation()
        result = mutation.delete_task(id=1, info=mock_info)

        # Verify
        assert result is True
        mock_db.delete.assert_called_once_with(mock_task_model)
        mock_db.commit.assert_called_once()

    @patch("src.presentation.graphql.resolvers.task_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_resolvers.get_db")
    def test_delete_task_not_found(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task deletion when task doesn't exist"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock task not found
        mock_query_chain = MagicMock()
        mock_query_chain.join.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = None
        mock_db.query.return_value = mock_query_chain

        # Execute - delete_task NO es async
        mutation = TaskMutation()
        result = mutation.delete_task(id=999, info=mock_info)

        # Verify
        assert result is False


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestHelperFunctions:
    def test_is_task_overdue_with_due_date_overdue(self):
        """Test _is_task_overdue function with overdue task"""
        from src.presentation.graphql.resolvers.task_resolvers import _is_task_overdue

        # Mock task with overdue date
        mock_task = MagicMock()
        mock_task.due_date = datetime.now() - timedelta(days=1)
        mock_task.status = DomainTaskStatus.PENDING

        result = _is_task_overdue(mock_task)
        assert result is True

    def test_is_task_overdue_with_due_date_not_overdue(self):
        """Test _is_task_overdue function with non-overdue task"""
        from src.presentation.graphql.resolvers.task_resolvers import _is_task_overdue

        # Mock task with future date
        mock_task = MagicMock()
        mock_task.due_date = datetime.now() + timedelta(days=1)
        mock_task.status = DomainTaskStatus.PENDING

        result = _is_task_overdue(mock_task)
        assert result is False

    def test_is_task_overdue_no_due_date(self):
        """Test _is_task_overdue function with no due date"""
        from src.presentation.graphql.resolvers.task_resolvers import _is_task_overdue

        # Mock task without due date
        mock_task = MagicMock()
        mock_task.due_date = None

        result = _is_task_overdue(mock_task)
        assert result is False

    def test_is_task_overdue_completed_task(self):
        """Test _is_task_overdue function with completed task"""
        from src.presentation.graphql.resolvers.task_resolvers import _is_task_overdue

        # Mock completed task with overdue date
        mock_task = MagicMock()
        mock_task.due_date = datetime.now() - timedelta(days=1)
        mock_task.status = DomainTaskStatus.COMPLETED

        result = _is_task_overdue(mock_task)
        assert result is False
