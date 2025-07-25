from datetime import datetime
from unittest.mock import Mock

import pytest

from src.application.dto import (
    TaskListCreateDTO,
    TaskListResponseDTO,
    TaskListUpdateDTO,
)
from src.application.services import TaskListService
from src.domain.entities import TaskList


def test_task_list_create_basic():
    task_list = TaskListCreateDTO(
        name="Work Tasks", description="Tasks for work projects"
    )
    assert task_list.name == "Work Tasks"
    assert task_list.description == "Tasks for work projects"


def test_task_list_create_minimal():
    task_list = TaskListCreateDTO(name="Minimal List")
    assert task_list.name == "Minimal List"
    assert task_list.description is None


def test_task_list_update():
    task_list_update = TaskListUpdateDTO(
        name="Updated List Name", description="Updated description"
    )
    assert task_list_update.name == "Updated List Name"
    assert task_list_update.description == "Updated description"


def test_task_list_update_partial():
    task_list_update = TaskListUpdateDTO(name="Only Name Updated")
    assert task_list_update.name == "Only Name Updated"
    assert task_list_update.description is None


def test_task_list_entity():
    now = datetime.now()
    task_list_data = {
        "id": 1,
        "name": "Personal Tasks",
        "description": "My personal task list",
        "owner_id": 123,
        "created_at": now,
        "updated_at": now,
    }
    task_list = TaskList(**task_list_data)
    assert task_list.id == 1
    assert task_list.name == "Personal Tasks"
    assert task_list.description == "My personal task list"
    assert task_list.owner_id == 123
    assert task_list.created_at == now


def test_task_list_create_dto():
    dto = TaskListCreateDTO(name="DTO Task List", description="DTO Description")
    assert dto.name == "DTO Task List"
    assert dto.description == "DTO Description"


def test_task_list_update_dto():
    dto = TaskListUpdateDTO(
        name="Updated DTO List", description="Updated DTO Description"
    )
    assert dto.name == "Updated DTO List"
    assert dto.description == "Updated DTO Description"


def test_task_list_response_dto():
    now = datetime.now()
    dto = TaskListResponseDTO(
        id=1,
        name="Response List",
        description="Response Description",
        owner_id=123,
        created_at=now,
        updated_at=now,
        completion_percentage=75.5,
        task_count=10,
    )
    assert dto.id == 1
    assert dto.name == "Response List"
    assert dto.owner_id == 123
    assert dto.completion_percentage == 75.5
    assert dto.task_count == 10


def test_task_list_service_instantiation():
    """Test that TaskListService can be instantiated"""
    mock_db = Mock()
    task_list_service = TaskListService(mock_db)
    assert task_list_service is not None


def test_task_list_name_required():
    """Test that task list name is required"""
    with pytest.raises(Exception):  # Pydantic will raise validation error
        TaskListCreateDTO(name="")


def test_task_list_description_optional():
    """Test that description is optional"""
    task_list = TaskListCreateDTO(name="List without description")
    assert task_list.name == "List without description"
    assert task_list.description is None


def test_task_list_name_length():
    """Test task list with different name lengths"""
    # Short name
    short_list = TaskListCreateDTO(name="A")
    assert short_list.name == "A"

    # Long name
    long_name = "A" * 100
    long_list = TaskListCreateDTO(name=long_name)
    assert long_list.name == long_name


def test_task_list_completion_percentage_calculation():
    """Test that completion percentage is properly handled in response"""
    dto = TaskListResponseDTO(
        id=1,
        name="Test List",
        description="Test",
        owner_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        completion_percentage=33.3,
        task_count=3,
    )
    assert dto.completion_percentage == 33.3
    assert isinstance(dto.completion_percentage, float)
