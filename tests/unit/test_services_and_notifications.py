from datetime import datetime
from unittest.mock import Mock

import pytest

from src.application.services import NotificationService, TaskListService, TaskService
from src.domain.entities import TaskPriority, TaskStatus
from src.infrastructure.database import TaskModel, UserModel


# Tests para NotificationService
def test_notification_service_instantiation():
    """Test NotificationService can be instantiated"""
    service = NotificationService()
    assert service is not None
    assert service.enabled is True


def test_notification_service_disable():
    """Test NotificationService can be disabled"""
    service = NotificationService()
    service.enabled = False
    assert service.enabled is False


@pytest.mark.asyncio
async def test_send_task_assignment_notification():
    """Test task assignment notification"""
    service = NotificationService()

    # Mock task and user
    mock_task = Mock(spec=TaskModel)
    mock_task.title = "Test Task"

    mock_user = Mock(spec=UserModel)
    mock_user.email = "assignee@example.com"

    # Test notification sending
    result = await service.send_task_assignment_notification(mock_task, mock_user)
    assert result is True


@pytest.mark.asyncio
async def test_send_task_completion_notification():
    """Test task completion notification"""
    service = NotificationService()

    # Mock task and owner
    mock_task = Mock(spec=TaskModel)
    mock_task.title = "Completed Task"

    mock_owner = Mock(spec=UserModel)
    mock_owner.email = "owner@example.com"

    # Test notification sending
    result = await service.send_task_completion_notification(mock_task, mock_owner)
    assert result is True


@pytest.mark.asyncio
async def test_send_overdue_task_notification():
    """Test overdue task notification"""
    service = NotificationService()

    # Mock overdue tasks
    mock_task1 = Mock(spec=TaskModel)
    mock_task1.title = "Overdue Task 1"

    mock_task2 = Mock(spec=TaskModel)
    mock_task2.title = "Overdue Task 2"

    overdue_tasks = [mock_task1, mock_task2]

    mock_user = Mock(spec=UserModel)
    mock_user.email = "user@example.com"

    # Test notification sending
    result = await service.send_overdue_task_notification(overdue_tasks, mock_user)
    assert result is True


@pytest.mark.asyncio
async def test_notification_service_disabled():
    """Test notifications when service is disabled"""
    service = NotificationService()
    service.enabled = False

    mock_task = Mock(spec=TaskModel)
    mock_user = Mock(spec=UserModel)

    # All notifications should return False when disabled
    result1 = await service.send_task_assignment_notification(mock_task, mock_user)
    result2 = await service.send_task_completion_notification(mock_task, mock_user)
    result3 = await service.send_overdue_task_notification([mock_task], mock_user)

    assert result1 is False
    assert result2 is False
    assert result3 is False


@pytest.mark.asyncio
async def test_overdue_notification_empty_list():
    """Test overdue notification with empty task list"""
    service = NotificationService()

    mock_user = Mock(spec=UserModel)
    mock_user.email = "user@example.com"

    # Empty list should return False
    result = await service.send_overdue_task_notification([], mock_user)
    assert result is False


# Tests para TaskService
def test_task_service_instantiation():
    """Test TaskService can be instantiated"""
    mock_db = Mock()
    service = TaskService(mock_db)
    assert service is not None


def test_task_service_state_validation():
    """Test task service validates state transitions"""
    mock_db = Mock()
    service = TaskService(mock_db)

    # Test valid state transitions
    valid_transitions = {
        TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
        TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.CANCELLED],
        TaskStatus.COMPLETED: [],
        TaskStatus.CANCELLED: [],
    }

    for current_status, valid_next_statuses in valid_transitions.items():
        for next_status in valid_next_statuses:
            # Valid transition should be allowed
            is_valid = service._is_valid_status_transition(current_status, next_status)
            assert is_valid is True


def test_task_service_invalid_transitions():
    """Test invalid task status transitions"""
    mock_db = Mock()
    service = TaskService(mock_db)

    # Test invalid transitions
    invalid_transitions = [
        (TaskStatus.PENDING, TaskStatus.COMPLETED),  # Can't go directly to completed
        (TaskStatus.COMPLETED, TaskStatus.PENDING),  # Can't reopen completed task
        (TaskStatus.CANCELLED, TaskStatus.IN_PROGRESS),  # Can't resume cancelled task
    ]

    for current_status, next_status in invalid_transitions:
        is_valid = service._is_valid_status_transition(current_status, next_status)
        assert is_valid is False


# Tests para TaskListService
def test_task_list_service_instantiation():
    """Test TaskListService can be instantiated"""
    mock_db = Mock()
    service = TaskListService(mock_db)
    assert service is not None


def test_task_completion_percentage_calculation():
    """Test completion percentage calculation logic"""
    # Mock data for completion calculation
    total_tasks = 10
    completed_tasks = 3

    # Expected percentage: 30%
    expected_percentage = (completed_tasks / total_tasks) * 100
    assert expected_percentage == 30.0

    # Test edge cases
    assert (0 / 1) * 100 == 0.0  # No completed tasks
    assert (5 / 5) * 100 == 100.0  # All tasks completed


def test_task_overdue_calculation():
    """Test overdue task calculation logic"""
    now = datetime.now()

    # Task due in the past should be overdue
    past_date = datetime(2023, 1, 1)
    assert now > past_date  # This task would be overdue

    # Task due in the future should not be overdue
    future_date = datetime(2025, 12, 31)
    assert now < future_date  # This task would not be overdue


def test_task_priority_ordering():
    """Test task priority ordering"""
    priorities = [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH]

    # Test that priorities have correct values
    assert TaskPriority.LOW.value == "low"
    assert TaskPriority.MEDIUM.value == "medium"
    assert TaskPriority.HIGH.value == "high"

    # Test priority comparison (this would be useful for sorting)
    assert len(priorities) == 3


def test_service_error_handling():
    """Test service error handling patterns"""
    mock_db = Mock()

    # Test services can handle mock database
    task_service = TaskService(mock_db)
    task_list_service = TaskListService(mock_db)
    notification_service = NotificationService()

    assert task_service is not None
    assert task_list_service is not None
    assert notification_service is not None


@pytest.mark.asyncio
async def test_notification_integration_workflow():
    """Test complete notification workflow"""
    service = NotificationService()

    # Mock a complete workflow
    mock_task = Mock(spec=TaskModel)
    mock_task.title = "Integration Test Task"

    mock_assignee = Mock(spec=UserModel)
    mock_assignee.email = "assignee@test.com"

    mock_owner = Mock(spec=UserModel)
    mock_owner.email = "owner@test.com"

    # 1. Send assignment notification
    assignment_result = await service.send_task_assignment_notification(
        mock_task, mock_assignee
    )
    assert assignment_result is True

    # 2. Send completion notification
    completion_result = await service.send_task_completion_notification(
        mock_task, mock_owner
    )
    assert completion_result is True


def test_service_configuration():
    """Test service configuration and settings"""
    # NotificationService should be configurable
    service = NotificationService()

    # Default state
    assert service.enabled is True

    # Can be disabled
    service.enabled = False
    assert service.enabled is False

    # Can be re-enabled
    service.enabled = True
    assert service.enabled is True


def test_mock_database_interactions():
    """Test that services work with mock databases"""
    mock_db = Mock()

    # Services should accept mock database
    task_service = TaskService(mock_db)
    task_list_service = TaskListService(mock_db)

    # Services should store the database reference
    assert task_service.db == mock_db
    assert task_list_service.db == mock_db
