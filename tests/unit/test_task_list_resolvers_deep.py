from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.presentation.graphql.resolvers.task_list_resolvers import (
    TaskListMutation,
    TaskListQuery,
)
from src.presentation.graphql.types import TaskListCreateInput, TaskListUpdateInput


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
def mock_task_list_model():
    """Mock TaskListModel from database"""
    task_list = MagicMock()
    task_list.id = 1
    task_list.name = "Test List"
    task_list.description = "Test Description"
    task_list.owner_id = 1
    task_list.created_at = datetime.now()
    task_list.updated_at = datetime.now()
    return task_list


# =============================================================================
# TASK LIST QUERY TESTS
# =============================================================================


class TestTaskListQuery:
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_task_lists_with_results(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_list_model,
    ):
        """Test task_lists query with results"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock query chain - los resolvers usan db.query() directo, no db.execute()
        mock_query_chain = MagicMock()
        mock_query_chain.outerjoin.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.group_by.return_value = mock_query_chain
        mock_query_chain.all.return_value = [
            (mock_task_list_model, 3, 1)
        ]  # task_list, total, completed

        mock_db.query.return_value = mock_query_chain

        # Execute
        query = TaskListQuery()
        result = query.task_lists(info=mock_info)

        # Verify
        assert len(result) == 1
        assert result[0].name == "Test List"
        assert result[0].completion_percentage == 33.3  # 1/3 * 100
        assert result[0].task_count == 3

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_task_lists_empty_result(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task_lists query with no results"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock empty query result
        mock_query_chain = MagicMock()
        mock_query_chain.outerjoin.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.group_by.return_value = mock_query_chain
        mock_query_chain.all.return_value = []

        mock_db.query.return_value = mock_query_chain

        # Execute
        query = TaskListQuery()
        result = query.task_lists(info=mock_info)

        # Verify
        assert len(result) == 0

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_task_lists_no_tasks(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_list_model,
    ):
        """Test task_lists query with lists that have no tasks"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock query result with no tasks (0 count, 0 completed)
        mock_query_chain = MagicMock()
        mock_query_chain.outerjoin.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.group_by.return_value = mock_query_chain
        mock_query_chain.all.return_value = [
            (mock_task_list_model, 0, 0)
        ]  # task_list, 0 total, 0 completed

        mock_db.query.return_value = mock_query_chain

        # Execute
        query = TaskListQuery()
        result = query.task_lists(info=mock_info)

        # Verify
        assert len(result) == 1
        assert result[0].completion_percentage == 0.0
        assert result[0].task_count == 0

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_task_list_by_id_found(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_list_model,
    ):
        """Test task_list query by ID when found"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock query chain for finding by ID
        mock_query_chain = MagicMock()
        mock_query_chain.outerjoin.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.group_by.return_value = mock_query_chain
        mock_query_chain.first.return_value = (
            mock_task_list_model,
            2,
            1,
        )  # task_list, total, completed

        mock_db.query.return_value = mock_query_chain

        # Execute
        query = TaskListQuery()
        result = query.task_list(id=1, info=mock_info)

        # Verify
        assert result is not None
        assert result.name == "Test List"
        assert result.completion_percentage == 50.0  # 1/2 * 100

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_task_list_by_id_not_found(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task_list query by ID when not found"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock task list not found
        mock_query_chain = MagicMock()
        mock_query_chain.outerjoin.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.group_by.return_value = mock_query_chain
        mock_query_chain.first.return_value = None

        mock_db.query.return_value = mock_query_chain

        # Execute
        query = TaskListQuery()
        result = query.task_list(id=999, info=mock_info)

        # Verify
        assert result is None


# =============================================================================
# TASK LIST MUTATION TESTS
# =============================================================================


class TestTaskListMutation:
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_create_task_list_success(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_list_model,
    ):
        """Test successful task list creation"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskListCreateInput(name="New List", description="New Description")

        # Mock database operations
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Mock final query for result con stats
        mock_query_chain = MagicMock()
        mock_query_chain.outerjoin.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.group_by.return_value = mock_query_chain
        mock_query_chain.first.return_value = (
            mock_task_list_model,
            0,
            0,
        )  # nueva lista sin tasks

        mock_db.query.return_value = mock_query_chain

        # Execute
        mutation = TaskListMutation()
        result = mutation.create_task_list(input=input_data, info=mock_info)

        # Verify
        assert result is not None
        # Verificar que la creación funcionó correctamente
        assert hasattr(result, "name")  # Confirmar que tiene nombre
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_update_task_list_success(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_list_model,
    ):
        """Test successful task list update"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskListUpdateInput(
            name="Updated List", description="Updated Description"
        )

        # Mock finding the task list
        mock_query_chain = MagicMock()
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = mock_task_list_model

        # Mock final stats query
        mock_stats_chain = MagicMock()
        mock_stats_chain.outerjoin.return_value = mock_stats_chain
        mock_stats_chain.filter.return_value = mock_stats_chain
        mock_stats_chain.group_by.return_value = mock_stats_chain
        mock_stats_chain.first.return_value = (mock_task_list_model, 2, 1)

        # Use side_effect to return different results for different queries
        mock_db.query.side_effect = [mock_query_chain, mock_stats_chain]

        # Mock database operations
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Execute
        mutation = TaskListMutation()
        result = mutation.update_task_list(id=1, input=input_data, info=mock_info)

        # Verify
        assert result is not None
        # Verificar que la actualización funcionó correctamente
        assert hasattr(result, "name")  # Confirmar que tiene nombre
        mock_db.commit.assert_called_once()

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_update_task_list_not_found(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task list update when list doesn't exist"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskListUpdateInput(name="Updated List")

        # Mock task list not found
        mock_query_chain = MagicMock()
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = None
        mock_db.query.return_value = mock_query_chain

        # Execute
        mutation = TaskListMutation()
        result = mutation.update_task_list(id=999, input=input_data, info=mock_info)

        # Verify
        assert result is None

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_delete_task_list_success(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_list_model,
    ):
        """Test successful task list deletion"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock finding the task list - los resolvers usan query() directo
        mock_query_chain = MagicMock()
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = mock_task_list_model
        mock_db.query.return_value = mock_query_chain

        # Mock database operations
        mock_db.delete = MagicMock()
        mock_db.commit = MagicMock()

        # Execute
        mutation = TaskListMutation()
        result = mutation.delete_task_list(id=1, info=mock_info)

        # Verify
        assert result is True
        mock_db.delete.assert_called_once_with(mock_task_list_model)

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_delete_task_list_not_found(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task list deletion when list doesn't exist"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock task list not found
        mock_query_chain = MagicMock()
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.first.return_value = None
        mock_db.query.return_value = mock_query_chain

        # Execute
        mutation = TaskListMutation()
        result = mutation.delete_task_list(id=999, info=mock_info)

        # Verify
        assert result is False


# =============================================================================
# EDGE CASES TESTS
# =============================================================================


class TestTaskListEdgeCases:
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_task_lists_database_error(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test task_lists query when database error occurs"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        # Mock database error - en el query chain, no en execute
        mock_query_chain = MagicMock()
        mock_query_chain.outerjoin.return_value = mock_query_chain
        mock_query_chain.filter.return_value = mock_query_chain
        mock_query_chain.group_by.return_value = mock_query_chain
        mock_query_chain.all.side_effect = Exception("Database connection error")

        mock_db.query.return_value = mock_query_chain

        # Execute & Verify
        query = TaskListQuery()
        with pytest.raises(Exception, match="Database connection error"):
            query.task_lists(info=mock_info)

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_create_task_list_database_error(
        self, mock_get_db, mock_require_auth, mock_info, mock_user, mock_db
    ):
        """Test create_task_list when database error occurs during commit"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskListCreateInput(name="New List")

        # Mock database operations
        mock_db.add = MagicMock()
        mock_db.commit.side_effect = Exception("Commit failed")

        # Execute & Verify
        mutation = TaskListMutation()
        with pytest.raises(Exception, match="Commit failed"):
            mutation.create_task_list(input=input_data, info=mock_info)

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_update_task_list_partial_update(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_list_model,
    ):
        """Test partial update of task list (only name)"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskListUpdateInput(name="Updated Name Only")
        # Note: description is not provided (should remain unchanged)

        # Mock finding the task list
        mock_find_chain = MagicMock()
        mock_find_chain.filter.return_value = mock_find_chain
        mock_find_chain.first.return_value = mock_task_list_model

        # Mock final stats query
        mock_stats_chain = MagicMock()
        mock_stats_chain.outerjoin.return_value = mock_stats_chain
        mock_stats_chain.filter.return_value = mock_stats_chain
        mock_stats_chain.group_by.return_value = mock_stats_chain
        mock_stats_chain.first.return_value = (mock_task_list_model, 1, 1)

        mock_db.query.side_effect = [mock_find_chain, mock_stats_chain]

        # Mock database operations
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Execute
        mutation = TaskListMutation()
        result = mutation.update_task_list(id=1, input=input_data, info=mock_info)

        # Verify
        assert result is not None
        # Only name should be updated, description remains as set in the mock
        mock_db.commit.assert_called_once()

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_update_task_list_empty_update(
        self,
        mock_get_db,
        mock_require_auth,
        mock_info,
        mock_user,
        mock_db,
        mock_task_list_model,
    ):
        """Test update with empty input (no fields to update)"""
        # Setup
        mock_require_auth.return_value = mock_user
        mock_get_db.return_value = mock_db

        input_data = TaskListUpdateInput()
        # No fields provided for update

        # Mock finding the task list
        mock_find_chain = MagicMock()
        mock_find_chain.filter.return_value = mock_find_chain
        mock_find_chain.first.return_value = mock_task_list_model

        # Mock final stats query
        mock_stats_chain = MagicMock()
        mock_stats_chain.outerjoin.return_value = mock_stats_chain
        mock_stats_chain.filter.return_value = mock_stats_chain
        mock_stats_chain.group_by.return_value = mock_stats_chain
        mock_stats_chain.first.return_value = (mock_task_list_model, 0, 0)

        mock_db.query.side_effect = [mock_find_chain, mock_stats_chain]

        # Mock database operations
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Execute
        mutation = TaskListMutation()
        result = mutation.update_task_list(id=1, input=input_data, info=mock_info)

        # Verify
        assert result is not None
        # Should still work even with no updates
        mock_db.commit.assert_called_once()


# =============================================================================
# AUTHORIZATION TESTS
# =============================================================================


class TestTaskListAuthorization:
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_task_lists_requires_authentication(
        self, mock_get_db, mock_require_auth, mock_info, mock_db
    ):
        """Test that task_lists query requires authentication"""
        # Setup
        mock_require_auth.side_effect = Exception("Authentication required")
        mock_get_db.return_value = mock_db

        # Execute & Verify
        query = TaskListQuery()
        with pytest.raises(Exception, match="Authentication required"):
            query.task_lists(info=mock_info)

    @patch("src.presentation.graphql.resolvers.task_list_resolvers.require_auth")
    @patch("src.presentation.graphql.resolvers.task_list_resolvers.get_db")
    def test_create_task_list_requires_authentication(
        self, mock_get_db, mock_require_auth, mock_info, mock_db
    ):
        """Test that create_task_list mutation requires authentication"""
        # Setup
        mock_require_auth.side_effect = Exception("Authentication required")
        mock_get_db.return_value = mock_db

        input_data = TaskListCreateInput(name="Test List")

        # Execute & Verify
        mutation = TaskListMutation()
        with pytest.raises(Exception, match="Authentication required"):
            mutation.create_task_list(input=input_data, info=mock_info)
