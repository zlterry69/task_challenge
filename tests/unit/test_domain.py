from datetime import datetime

from src.application.dto import (
    TaskCreateDTO,
    TaskListCreateDTO,
    TaskListUpdateDTO,
    TaskUpdateDTO,
    UserCreateDTO,
    UserUpdateDTO,
)
from src.domain.entities import Task, TaskList, TaskPriority, TaskStatus, User
from src.domain.exceptions import (
    BusinessRuleError,
    EntityNotFoundError,
    UnauthorizedError,
    ValidationError,
)


# Tests para User entities
def test_user_create_validation():
    user = UserCreateDTO(
        email="test@example.com", full_name="Test User", password="secret123"
    )
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.password == "secret123"


def test_user_update_validation():
    user_update = UserUpdateDTO(full_name="Updated Name")
    assert user_update.full_name == "Updated Name"
    assert user_update.email is None


def test_user_entity():
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": "hashedpass",
        "is_active": True,
    }
    user = User(**user_data)
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.is_active is True


# Tests para Task entities
def test_task_status_enum():
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.CANCELLED.value == "cancelled"


def test_task_priority_enum():
    assert TaskPriority.LOW.value == "low"
    assert TaskPriority.MEDIUM.value == "medium"
    assert TaskPriority.HIGH.value == "high"


def test_task_create_validation():
    task = TaskCreateDTO(
        title="Test Task",
        description="Test description",
        task_list_id=1,
        priority=TaskPriority.HIGH,
        assigned_to=2,
    )
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.task_list_id == 1
    assert task.priority == TaskPriority.HIGH
    assert task.assigned_to == 2


def test_task_update_validation():
    task_update = TaskUpdateDTO(title="Updated Task")
    assert task_update.title == "Updated Task"
    assert task_update.description is None


def test_task_entity():
    task_data = {
        "id": 1,
        "title": "Test Task",
        "description": "Description",
        "status": TaskStatus.PENDING,
        "priority": TaskPriority.MEDIUM,
        "task_list_id": 1,
        "assigned_to": 2,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    task = Task(**task_data)
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.status == TaskStatus.PENDING


# Tests para TaskList entities
def test_task_list_create_validation():
    task_list = TaskListCreateDTO(
        name="Work Tasks", description="Tasks for work projects"
    )
    assert task_list.name == "Work Tasks"
    assert task_list.description == "Tasks for work projects"


def test_task_list_update_validation():
    task_list_update = TaskListUpdateDTO(name="Updated Name")
    assert task_list_update.name == "Updated Name"
    assert task_list_update.description is None


def test_task_list_entity():
    task_list_data = {
        "id": 1,
        "name": "Personal Tasks",
        "description": "My personal tasks",
        "owner_id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    task_list = TaskList(**task_list_data)
    assert task_list.id == 1
    assert task_list.name == "Personal Tasks"
    assert task_list.owner_id == 1


# Tests para DTOs
def test_user_create_dto():
    dto = UserCreateDTO(
        email="dto@example.com", full_name="DTO User", password="password123"
    )
    assert dto.email == "dto@example.com"
    assert dto.full_name == "DTO User"


def test_task_create_dto():
    dto = TaskCreateDTO(
        title="DTO Task",
        description="DTO Description",
        task_list_id=1,
        priority=TaskPriority.HIGH,
    )
    assert dto.title == "DTO Task"
    assert dto.task_list_id == 1
    assert dto.priority == TaskPriority.HIGH


def test_task_list_create_dto():
    dto = TaskListCreateDTO(name="DTO Task List", description="DTO Description")
    assert dto.name == "DTO Task List"
    assert dto.description == "DTO Description"


# Tests para Custom Exceptions
def test_validation_error():
    error = ValidationError("Invalid input", field="email")
    assert str(error) == "Invalid input"
    assert error.message == "Invalid input"
    assert error.code == "VALIDATION_ERROR"
    assert error.field == "email"


def test_entity_not_found_error():
    error = EntityNotFoundError("Task", entity_id="123")
    assert "Task not found" in str(error)
    assert error.code == "ENTITY_NOT_FOUND"
    assert error.message.startswith("Task not found")


def test_unauthorized_error():
    error = UnauthorizedError("Access denied")
    assert str(error) == "Access denied"
    assert error.message == "Access denied"
    assert error.code == "UNAUTHORIZED"


def test_business_rule_error():
    error = BusinessRuleError("Business rule violated", rule="NO_DELETE")
    assert str(error) == "Business rule violated"
    assert error.message == "Business rule violated"
    assert error.code == "BUSINESS_RULE_ERROR"
    assert error.rule == "NO_DELETE"
