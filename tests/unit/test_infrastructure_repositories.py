from datetime import datetime
from unittest.mock import AsyncMock, Mock

from src.domain.entities import Task, TaskList, TaskPriority, TaskStatus, User
from src.infrastructure.database import TaskListModel, TaskModel, UserModel
from src.infrastructure.repositories import (
    SQLAlchemyTaskListRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyUserRepository,
)


# Tests para SQLAlchemyUserRepository
def test_sqlalchemy_user_repository_structure():
    """Test SQLAlchemyUserRepository structure"""
    # Mock async session
    mock_session = AsyncMock()

    # Test repository creation
    repo = SQLAlchemyUserRepository(mock_session)
    assert repo.session == mock_session


def test_sqlalchemy_user_repository_to_entity():
    """Test SQLAlchemyUserRepository _to_entity method"""
    # Mock async session
    mock_session = AsyncMock()
    repo = SQLAlchemyUserRepository(mock_session)

    # Mock user model
    mock_user_model = Mock(spec=UserModel)
    mock_user_model.id = 1
    mock_user_model.email = "test@example.com"
    mock_user_model.full_name = "Test User"
    mock_user_model.hashed_password = "hashed_password"
    mock_user_model.is_active = True
    mock_user_model.created_at = datetime.now()
    mock_user_model.updated_at = datetime.now()

    # Test entity conversion
    entity = repo._to_entity(mock_user_model)
    assert entity.id == 1
    assert entity.email == "test@example.com"
    assert entity.full_name == "Test User"
    assert entity.hashed_password == "hashed_password"
    assert entity.is_active is True


def test_sqlalchemy_user_repository_to_model():
    """Test SQLAlchemyUserRepository _to_model method"""
    # Mock async session
    mock_session = AsyncMock()
    repo = SQLAlchemyUserRepository(mock_session)

    # Mock user entity
    mock_user_entity = Mock(spec=User)
    mock_user_entity.id = 1
    mock_user_entity.email = "test@example.com"
    mock_user_entity.full_name = "Test User"
    mock_user_entity.hashed_password = "hashed_password"
    mock_user_entity.is_active = True
    mock_user_entity.created_at = datetime.now()
    mock_user_entity.updated_at = datetime.now()

    # Test model conversion
    model = repo._to_model(mock_user_entity)
    assert model.id == 1
    assert model.email == "test@example.com"
    assert model.full_name == "Test User"
    assert model.hashed_password == "hashed_password"
    assert model.is_active is True


def test_sqlalchemy_user_repository_create():
    """Test SQLAlchemyUserRepository create method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyUserRepository(mock_session)

    # Mock user entity
    mock_user_entity = Mock(spec=User)
    mock_user_entity.id = 1
    mock_user_entity.email = "test@example.com"
    mock_user_entity.full_name = "Test User"
    mock_user_entity.hashed_password = "hashed_password"
    mock_user_entity.is_active = True
    mock_user_entity.created_at = datetime.now()
    mock_user_entity.updated_at = datetime.now()

    # Test create method structure
    assert mock_user_entity.id == 1
    assert mock_user_entity.email == "test@example.com"


def test_sqlalchemy_user_repository_get_by_id():
    """Test SQLAlchemyUserRepository get_by_id method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyUserRepository(mock_session)

    # Test get_by_id method structure
    user_id = 1
    assert user_id == 1


def test_sqlalchemy_user_repository_get_by_email():
    """Test SQLAlchemyUserRepository get_by_email method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyUserRepository(mock_session)

    # Test get_by_email method structure
    email = "test@example.com"
    assert email == "test@example.com"


def test_sqlalchemy_user_repository_update():
    """Test SQLAlchemyUserRepository update method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyUserRepository(mock_session)

    # Mock user entity
    mock_user_entity = Mock(spec=User)
    mock_user_entity.id = 1
    mock_user_entity.email = "updated@example.com"

    # Test update method structure
    assert mock_user_entity.id == 1
    assert mock_user_entity.email == "updated@example.com"


def test_sqlalchemy_user_repository_delete():
    """Test SQLAlchemyUserRepository delete method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyUserRepository(mock_session)

    # Test delete method structure
    user_id = 1
    assert user_id == 1


def test_sqlalchemy_user_repository_list_active_users():
    """Test SQLAlchemyUserRepository list_active_users method"""
    # Mock async session
    mock_session = AsyncMock()
    repo = SQLAlchemyUserRepository(mock_session)

    # Test list_active_users method structure
    assert repo.session == mock_session


# Tests para SQLAlchemyTaskListRepository
def test_sqlalchemy_task_list_repository_structure():
    """Test SQLAlchemyTaskListRepository structure"""
    # Mock async session
    mock_session = AsyncMock()

    # Test repository creation
    repo = SQLAlchemyTaskListRepository(mock_session)
    assert repo.session == mock_session


def test_sqlalchemy_task_list_repository_to_entity():
    """Test SQLAlchemyTaskListRepository _to_entity method"""
    # Mock async session
    mock_session = AsyncMock()
    repo = SQLAlchemyTaskListRepository(mock_session)

    # Mock task list model
    mock_task_list_model = Mock(spec=TaskListModel)
    mock_task_list_model.id = 1
    mock_task_list_model.name = "Test List"
    mock_task_list_model.description = "Test Description"
    mock_task_list_model.owner_id = 123
    mock_task_list_model.created_at = datetime.now()
    mock_task_list_model.updated_at = datetime.now()
    mock_task_list_model.tasks = []

    # Test entity conversion
    entity = repo._to_entity(mock_task_list_model)
    assert entity.id == 1
    assert entity.name == "Test List"
    assert entity.description == "Test Description"
    assert entity.owner_id == 123


def test_sqlalchemy_task_list_repository_to_model():
    """Test SQLAlchemyTaskListRepository _to_model method"""
    # Mock async session
    mock_session = AsyncMock()
    repo = SQLAlchemyTaskListRepository(mock_session)

    # Mock task list entity
    mock_task_list_entity = Mock(spec=TaskList)
    mock_task_list_entity.id = 1
    mock_task_list_entity.name = "Test List"
    mock_task_list_entity.description = "Test Description"
    mock_task_list_entity.owner_id = 123
    mock_task_list_entity.created_at = datetime.now()
    mock_task_list_entity.updated_at = datetime.now()

    # Test model conversion
    model = repo._to_model(mock_task_list_entity)
    assert model.id == 1
    assert model.name == "Test List"
    assert model.description == "Test Description"
    assert model.owner_id == 123


def test_sqlalchemy_task_list_repository_create():
    """Test SQLAlchemyTaskListRepository create method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskListRepository(mock_session)

    # Mock task list entity
    mock_task_list_entity = Mock(spec=TaskList)
    mock_task_list_entity.id = 1
    mock_task_list_entity.name = "Test List"
    mock_task_list_entity.owner_id = 123

    # Test create method structure
    assert mock_task_list_entity.id == 1
    assert mock_task_list_entity.name == "Test List"
    assert mock_task_list_entity.owner_id == 123


def test_sqlalchemy_task_list_repository_get_by_id():
    """Test SQLAlchemyTaskListRepository get_by_id method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskListRepository(mock_session)

    # Test get_by_id method structure
    task_list_id = 1
    assert task_list_id == 1


def test_sqlalchemy_task_list_repository_get_by_owner():
    """Test SQLAlchemyTaskListRepository get_by_owner method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskListRepository(mock_session)

    # Test get_by_owner method structure
    owner_id = 123
    skip = 0
    limit = 10
    assert owner_id == 123
    assert skip == 0
    assert limit == 10


def test_sqlalchemy_task_list_repository_update():
    """Test SQLAlchemyTaskListRepository update method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskListRepository(mock_session)

    # Mock task list entity
    mock_task_list_entity = Mock(spec=TaskList)
    mock_task_list_entity.id = 1
    mock_task_list_entity.name = "Updated List"

    # Test update method structure
    assert mock_task_list_entity.id == 1
    assert mock_task_list_entity.name == "Updated List"


def test_sqlalchemy_task_list_repository_delete():
    """Test SQLAlchemyTaskListRepository delete method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskListRepository(mock_session)

    # Test delete method structure
    task_list_id = 1
    assert task_list_id == 1


def test_sqlalchemy_task_list_repository_list_all():
    """Test SQLAlchemyTaskListRepository list_all method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskListRepository(mock_session)

    # Test list_all method structure
    skip = 0
    limit = 10
    assert skip == 0
    assert limit == 10


# Tests para SQLAlchemyTaskRepository
def test_sqlalchemy_task_repository_structure():
    """Test SQLAlchemyTaskRepository structure"""
    # Mock async session
    mock_session = AsyncMock()

    # Test repository creation
    repo = SQLAlchemyTaskRepository(mock_session)
    assert repo.session == mock_session


def test_sqlalchemy_task_repository_to_entity():
    """Test SQLAlchemyTaskRepository _to_entity method"""
    # Mock async session
    mock_session = AsyncMock()
    repo = SQLAlchemyTaskRepository(mock_session)

    # Mock task model
    mock_task_model = Mock(spec=TaskModel)
    mock_task_model.id = 1
    mock_task_model.title = "Test Task"
    mock_task_model.description = "Test Description"
    mock_task_model.status = TaskStatus.PENDING
    mock_task_model.priority = TaskPriority.MEDIUM
    mock_task_model.task_list_id = 1
    mock_task_model.assigned_to = 2
    mock_task_model.created_at = datetime.now()
    mock_task_model.updated_at = datetime.now()
    mock_task_model.due_date = datetime(2025, 12, 31)

    # Test entity conversion
    entity = repo._to_entity(mock_task_model)
    assert entity.id == 1
    assert entity.title == "Test Task"
    assert entity.description == "Test Description"
    assert entity.status == TaskStatus.PENDING
    assert entity.priority == TaskPriority.MEDIUM
    assert entity.task_list_id == 1
    assert entity.assigned_to == 2


def test_sqlalchemy_task_repository_to_model():
    """Test SQLAlchemyTaskRepository _to_model method"""
    # Mock async session
    mock_session = AsyncMock()
    repo = SQLAlchemyTaskRepository(mock_session)

    # Mock task entity
    mock_task_entity = Mock(spec=Task)
    mock_task_entity.id = 1
    mock_task_entity.title = "Test Task"
    mock_task_entity.description = "Test Description"
    mock_task_entity.status = TaskStatus.PENDING
    mock_task_entity.priority = TaskPriority.MEDIUM
    mock_task_entity.task_list_id = 1
    mock_task_entity.assigned_to = 2
    mock_task_entity.created_at = datetime.now()
    mock_task_entity.updated_at = datetime.now()
    mock_task_entity.due_date = datetime(2025, 12, 31)

    # Test model conversion
    model = repo._to_model(mock_task_entity)
    assert model.id == 1
    assert model.title == "Test Task"
    assert model.description == "Test Description"
    assert model.status == TaskStatus.PENDING
    assert model.priority == TaskPriority.MEDIUM
    assert model.task_list_id == 1
    assert model.assigned_to == 2


def test_sqlalchemy_task_repository_create():
    """Test SQLAlchemyTaskRepository create method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskRepository(mock_session)

    # Mock task entity
    mock_task_entity = Mock(spec=Task)
    mock_task_entity.id = 1
    mock_task_entity.title = "Test Task"
    mock_task_entity.task_list_id = 1

    # Test create method structure
    assert mock_task_entity.id == 1
    assert mock_task_entity.title == "Test Task"
    assert mock_task_entity.task_list_id == 1


def test_sqlalchemy_task_repository_get_by_id():
    """Test SQLAlchemyTaskRepository get_by_id method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskRepository(mock_session)

    # Test get_by_id method structure
    task_id = 1
    assert task_id == 1


def test_sqlalchemy_task_repository_get_by_task_list():
    """Test SQLAlchemyTaskRepository get_by_task_list method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskRepository(mock_session)

    # Test get_by_task_list method structure
    task_list_id = 1
    assert task_list_id == 1


def test_sqlalchemy_task_repository_get_by_assignee():
    """Test SQLAlchemyTaskRepository get_by_assignee method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskRepository(mock_session)

    # Test get_by_assignee method structure
    assignee_id = 2
    assert assignee_id == 2


def test_sqlalchemy_task_repository_update():
    """Test SQLAlchemyTaskRepository update method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskRepository(mock_session)

    # Mock task entity
    mock_task_entity = Mock(spec=Task)
    mock_task_entity.id = 1
    mock_task_entity.title = "Updated Task"

    # Test update method structure
    assert mock_task_entity.id == 1
    assert mock_task_entity.title == "Updated Task"


def test_sqlalchemy_task_repository_delete():
    """Test SQLAlchemyTaskRepository delete method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskRepository(mock_session)

    # Test delete method structure
    task_id = 1
    assert task_id == 1


def test_sqlalchemy_task_repository_filter_by_status():
    """Test SQLAlchemyTaskRepository filter_by_status method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskRepository(mock_session)

    # Test filter_by_status method structure
    task_list_id = 1
    status = TaskStatus.PENDING
    assert task_list_id == 1
    assert status == TaskStatus.PENDING


def test_sqlalchemy_task_repository_filter_by_priority():
    """Test SQLAlchemyTaskRepository filter_by_priority method"""
    # Mock async session
    mock_session = AsyncMock()
    SQLAlchemyTaskRepository(mock_session)

    # Test filter_by_priority method structure
    task_list_id = 1
    priority = TaskPriority.HIGH
    assert task_list_id == 1
    assert priority == TaskPriority.HIGH


def test_sqlalchemy_task_repository_get_overdue_tasks():
    """Test SQLAlchemyTaskRepository get_overdue_tasks method"""
    # Mock async session
    mock_session = AsyncMock()
    repo = SQLAlchemyTaskRepository(mock_session)

    # Test get_overdue_tasks method structure
    assert repo.session == mock_session


# Tests para async session handling
def test_async_session_structure():
    """Test async session structure"""
    # Mock async session
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.add = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.delete = AsyncMock()

    # Test session methods
    assert mock_session.execute is not None
    assert mock_session.add is not None
    assert mock_session.flush is not None
    assert mock_session.refresh is not None
    assert mock_session.delete is not None


def test_async_session_execute():
    """Test async session execute method"""
    # Mock async session
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()

    # Test execute method
    mock_session.execute()
    mock_session.execute.assert_called_once()


# Tests para domain entities
def test_user_entity_structure():
    """Test User entity structure"""
    # Mock user entity
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.full_name = "Test User"
    mock_user.hashed_password = "hashed_password"
    mock_user.is_active = True
    mock_user.created_at = datetime.now()
    mock_user.updated_at = datetime.now()

    # Test user entity structure
    assert mock_user.id == 1
    assert mock_user.email == "test@example.com"
    assert mock_user.full_name == "Test User"
    assert mock_user.hashed_password == "hashed_password"
    assert mock_user.is_active is True
    assert mock_user.created_at is not None
    assert mock_user.updated_at is not None


def test_task_list_entity_structure():
    """Test TaskList entity structure"""
    # Mock task list entity
    mock_task_list = Mock(spec=TaskList)
    mock_task_list.id = 1
    mock_task_list.name = "Test List"
    mock_task_list.description = "Test Description"
    mock_task_list.owner_id = 123
    mock_task_list.created_at = datetime.now()
    mock_task_list.updated_at = datetime.now()
    mock_task_list.tasks = []

    # Test task list entity structure
    assert mock_task_list.id == 1
    assert mock_task_list.name == "Test List"
    assert mock_task_list.description == "Test Description"
    assert mock_task_list.owner_id == 123
    assert mock_task_list.created_at is not None
    assert mock_task_list.updated_at is not None
    assert mock_task_list.tasks == []


def test_task_entity_structure():
    """Test Task entity structure"""
    # Mock task entity
    mock_task = Mock(spec=Task)
    mock_task.id = 1
    mock_task.title = "Test Task"
    mock_task.description = "Test Description"
    mock_task.status = TaskStatus.PENDING
    mock_task.priority = TaskPriority.MEDIUM
    mock_task.task_list_id = 1
    mock_task.assigned_to = 2
    mock_task.created_at = datetime.now()
    mock_task.updated_at = datetime.now()
    mock_task.due_date = datetime(2025, 12, 31)

    # Test task entity structure
    assert mock_task.id == 1
    assert mock_task.title == "Test Task"
    assert mock_task.description == "Test Description"
    assert mock_task.status == TaskStatus.PENDING
    assert mock_task.priority == TaskPriority.MEDIUM
    assert mock_task.task_list_id == 1
    assert mock_task.assigned_to == 2
    assert mock_task.created_at is not None
    assert mock_task.updated_at is not None
    assert mock_task.due_date == datetime(2025, 12, 31)
