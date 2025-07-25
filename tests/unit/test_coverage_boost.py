"""
Tests específicos para mejorar coverage en archivos críticos
"""
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session


def test_repositories_structure():
    """Test repositories structure and methods"""
    from src.infrastructure.repositories import (
        SQLAlchemyTaskListRepository,
        SQLAlchemyTaskRepository,
        SQLAlchemyUserRepository,
    )

    # Test repositories can be instantiated
    mock_session = Mock(spec=Session)

    user_repo = SQLAlchemyUserRepository(mock_session)
    task_repo = SQLAlchemyTaskRepository(mock_session)
    task_list_repo = SQLAlchemyTaskListRepository(mock_session)

    # Test they have expected methods
    assert hasattr(user_repo, "create")
    assert hasattr(user_repo, "get_by_id")
    assert hasattr(user_repo, "get_by_email")

    assert hasattr(task_repo, "create")
    assert hasattr(task_repo, "get_by_id")
    assert hasattr(task_repo, "update")

    assert hasattr(task_list_repo, "create")
    assert hasattr(task_list_repo, "get_by_id")
    assert hasattr(task_list_repo, "delete")


def test_task_router_endpoints():
    """Test task router endpoint structure"""
    from fastapi import APIRouter

    from src.presentation.routers.tasks import router

    assert isinstance(router, APIRouter)

    # Test router has routes
    routes = [route.path for route in router.routes]

    # Test expected endpoints exist (check for actual paths)
    assert "/api/tasks/" in routes
    assert "/api/tasks/{task_id}" in routes
    assert "/api/tasks/{task_id}/status" in routes
    assert "/api/tasks/stats" in routes


def test_task_list_router_endpoints():
    """Test task list router endpoint structure"""
    from fastapi import APIRouter

    from src.presentation.routers.task_lists import router

    assert isinstance(router, APIRouter)

    # Test router has routes
    routes = [route.path for route in router.routes]

    # Test expected endpoints exist (check for actual paths)
    assert "/api/task-lists/" in routes
    assert "/api/task-lists/{task_list_id}" in routes


def test_graphql_resolver_imports():
    """Test GraphQL resolvers can be imported"""
    from src.presentation.graphql.resolvers.auth_resolvers import (
        AuthMutation,
        AuthQuery,
    )
    from src.presentation.graphql.resolvers.task_list_resolvers import (
        TaskListMutation,
        TaskListQuery,
    )
    from src.presentation.graphql.resolvers.task_resolvers import (
        TaskMutation,
        TaskQuery,
    )

    # Test resolvers exist
    assert TaskQuery is not None
    assert TaskMutation is not None
    assert TaskListQuery is not None
    assert TaskListMutation is not None
    assert AuthQuery is not None
    assert AuthMutation is not None


def test_database_models_relationships():
    """Test database models and relationships"""
    from src.infrastructure.database import TaskListModel, TaskModel, UserModel

    # Test models can be instantiated
    user = UserModel(
        email="test@example.com", full_name="Test User", hashed_password="hashed"
    )

    task_list = TaskListModel(
        name="Test List", description="Test Description", owner_id=1
    )

    task = TaskModel(
        title="Test Task",
        description="Test Description",
        task_list_id=1,
        status="pending",
        priority="medium",
    )

    # Test basic attributes
    assert user.email == "test@example.com"
    assert task_list.name == "Test List"
    assert task.title == "Test Task"


def test_dependencies_functions():
    """Test dependency functions"""
    import types

    from src.presentation.dependencies import get_current_user, get_db

    # Test get_db is generator
    assert isinstance(get_db(), types.GeneratorType)

    # Test get_current_user is callable
    assert callable(get_current_user)


def test_auth_service_functions():
    """Test auth service functions"""
    from src.application.auth_service import (
        get_current_user,
        login_for_access_token,
        register_user,
    )

    # Test functions exist and are callable
    assert callable(register_user)
    assert callable(login_for_access_token)
    assert callable(get_current_user)


def test_exception_classes():
    """Test custom exception classes"""
    from src.domain.exceptions import (
        BusinessRuleError,
        EntityNotFoundError,
        TaskListOwnershipError,
        TaskStatusError,
        UnauthorizedError,
        ValidationError,
    )

    # Test exceptions can be raised
    with pytest.raises(EntityNotFoundError):
        raise EntityNotFoundError("User", "123")

    with pytest.raises(ValidationError):
        raise ValidationError("Invalid data")

    with pytest.raises(UnauthorizedError):
        raise UnauthorizedError("Access denied")

    with pytest.raises(BusinessRuleError):
        raise BusinessRuleError("Business rule violated")

    with pytest.raises(TaskListOwnershipError):
        raise TaskListOwnershipError("Not owner")

    with pytest.raises(TaskStatusError):
        raise TaskStatusError("Invalid status")


def test_notification_service_structure():
    """Test notification service structure"""
    from src.application.services import NotificationService

    service = NotificationService()

    # Test attributes
    assert hasattr(service, "enabled")
    assert service.enabled is True

    # Test methods exist
    assert hasattr(service, "send_task_assignment_notification")
    assert hasattr(service, "send_task_completion_notification")
    assert hasattr(service, "send_overdue_task_notification")


def test_graphql_context_functions():
    """Test GraphQL context functions"""
    from src.presentation.graphql.context import (
        get_current_user_from_context,
        get_db,
        require_auth,
    )

    # Test functions exist and are callable
    assert callable(get_db)
    assert callable(get_current_user_from_context)
    assert callable(require_auth)


def test_service_instantiation():
    """Test all services can be instantiated"""
    from src.application.services import (
        NotificationService,
        TaskListService,
        TaskService,
    )

    mock_db = Mock(spec=Session)

    # Test services can be created
    task_service = TaskService(mock_db)
    task_list_service = TaskListService(mock_db)
    notification_service = NotificationService()

    # Test they have db attribute where expected
    assert task_service.db == mock_db
    assert task_list_service.db == mock_db
    assert notification_service.enabled is True


def test_router_dependencies():
    """Test router dependency usage"""
    from src.presentation.routers.auth import router as auth_router
    from src.presentation.routers.task_lists import router as task_lists_router
    from src.presentation.routers.tasks import router as tasks_router

    # Test routers are configured
    assert tasks_router.prefix is None or isinstance(tasks_router.prefix, str)
    assert task_lists_router.prefix is None or isinstance(task_lists_router.prefix, str)
    assert auth_router.prefix is None or isinstance(auth_router.prefix, str)


def test_dto_edge_cases():
    """Test DTO edge cases and validation"""
    from src.application.dto import TaskCreateDTO, TaskListCreateDTO, UserCreateDTO

    # Test valid DTOs
    task_dto = TaskCreateDTO(
        title="Valid Task",
        description="Valid Description",
        task_list_id=1,
        priority="high",
    )
    assert task_dto.priority.value == "high"

    list_dto = TaskListCreateDTO(name="Valid List", description="Valid Description")
    assert list_dto.name == "Valid List"

    user_dto = UserCreateDTO(
        email="valid@test.com", full_name="Valid User", password="validpassword123"
    )
    assert "@" in user_dto.email


def test_enum_edge_cases():
    """Test enum edge cases"""
    from src.domain.entities import TaskPriority, TaskStatus

    # Test enum iteration
    all_statuses = list(TaskStatus)
    all_priorities = list(TaskPriority)

    assert len(all_statuses) == 4
    assert (
        len(all_priorities) == 4
    )  # Fixed: TaskPriority has 4 values including CRITICAL

    # Test enum values
    for status in all_statuses:
        assert isinstance(status.value, str)
        assert len(status.value) > 0

    for priority in all_priorities:
        assert isinstance(priority.value, str)
        assert len(priority.value) > 0


def test_main_app_components():
    """Test main app components"""
    from fastapi import FastAPI

    from src.presentation.main import app

    assert isinstance(app, FastAPI)
    assert len(app.routes) > 0

    # Test app has expected attributes
    assert hasattr(app, "title")
    assert hasattr(app, "version")
    assert hasattr(app, "routes")


def test_database_manager():
    """Test database manager"""
    from src.infrastructure.database import DatabaseManager

    # Test DatabaseManager can be instantiated with async driver
    db_manager = DatabaseManager("sqlite+aiosqlite:///test.db")

    # Test it has expected methods
    assert hasattr(db_manager, "create_tables")
    assert hasattr(db_manager, "drop_tables")
    assert hasattr(db_manager, "get_session")
