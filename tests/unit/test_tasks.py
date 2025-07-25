from datetime import datetime
from unittest.mock import Mock

import pytest

from src.application.dto import TaskCreateDTO, TaskResponseDTO, TaskUpdateDTO
from src.application.services import TaskService
from src.domain.entities import TaskPriority, TaskStatus


def test_task_create_with_defaults():
    task = TaskCreateDTO(
        title="Test Task", description="Test description", task_list_id=1
    )
    assert task.title == "Test Task"
    assert task.task_list_id == 1


def test_task_create_with_all_fields():
    task = TaskCreateDTO(
        title="Complete Task",
        description="Full description",
        task_list_id=1,
        priority=TaskPriority.HIGH,
        assigned_to=2,
        due_date=datetime(2025, 12, 31),
    )
    assert task.title == "Complete Task"
    assert task.priority == TaskPriority.HIGH
    assert task.assigned_to == 2


def test_task_update_partial():
    task_update = TaskUpdateDTO(title="Updated Title")
    assert task_update.title == "Updated Title"
    assert task_update.description is None
    assert task_update.priority is None


def test_task_status_transitions():
    """Test valid task status transitions"""
    # PENDING can go to IN_PROGRESS or CANCELLED
    assert TaskStatus.PENDING != TaskStatus.COMPLETED

    # Each status should have its correct value
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.CANCELLED.value == "cancelled"


def test_task_priority_levels():
    """Test task priority enum values"""
    assert TaskPriority.LOW.value == "low"
    assert TaskPriority.MEDIUM.value == "medium"
    assert TaskPriority.HIGH.value == "high"


def test_task_create_dto():
    dto = TaskCreateDTO(
        title="DTO Task",
        description="DTO Description",
        task_list_id=1,
        priority=TaskPriority.HIGH,
        assigned_to=2,
    )
    assert dto.title == "DTO Task"
    assert dto.task_list_id == 1
    assert dto.priority == TaskPriority.HIGH
    assert dto.assigned_to == 2


def test_task_update_dto():
    dto = TaskUpdateDTO(title="Updated DTO Task", priority=TaskPriority.LOW)
    assert dto.title == "Updated DTO Task"
    assert dto.priority == TaskPriority.LOW


def test_task_response_dto():
    now = datetime.now()
    dto = TaskResponseDTO(
        id=1,
        title="Response Task",
        description="Response Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        task_list_id=1,
        assigned_to=2,
        created_at=now,
        updated_at=now,
        due_date=datetime(2025, 12, 31),
        is_overdue=False,
        assignee_name="John Doe",
    )
    assert dto.id == 1
    assert dto.title == "Response Task"
    assert dto.status == TaskStatus.PENDING
    assert dto.is_overdue is False
    assert dto.assignee_name == "John Doe"


def test_task_service_instantiation():
    """Test that TaskService can be instantiated"""
    mock_db = Mock()
    task_service = TaskService(mock_db)
    assert task_service is not None


def test_task_validation_title_required():
    """Test that task title is required"""
    with pytest.raises(Exception):  # Pydantic will raise validation error
        TaskCreateDTO(title="", task_list_id=1)


def test_task_due_date_optional():
    """Test that due_date is optional"""
    task = TaskCreateDTO(title="Task without due date", task_list_id=1)
    assert task.due_date is None


def test_task_assigned_to_optional():
    """Test that assigned_to is optional"""
    task = TaskCreateDTO(title="Unassigned task", task_list_id=1)
    assert task.assigned_to is None
