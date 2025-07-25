from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from src.application.dto import TaskListCreateDTO, TaskListUpdateDTO
from src.presentation.routers import task_lists


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    return MagicMock(id=1)


def test_create_task_list(mock_db, mock_user):
    # Crear un mock que simule el comportamiento de TaskListModel
    mock_task_list = MagicMock()
    mock_task_list.id = 1
    mock_task_list.name = "My List"
    mock_task_list.description = "Test description"
    mock_task_list.owner_id = mock_user.id
    mock_task_list.created_at = datetime.now()
    mock_task_list.updated_at = datetime.now()

    # Mock TaskListModel para que devuelva nuestro mock_task_list
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    # Mock para que cuando se cree TaskListModel, devuelva nuestro mock
    with pytest.MonkeyPatch().context() as m:
        m.setattr(
            "src.presentation.routers.task_lists.TaskListModel",
            lambda **kwargs: mock_task_list,
        )
        result = task_lists.create_task_list(
            TaskListCreateDTO(name="My List"), mock_db, mock_user
        )
        assert result.name == "My List"


def test_get_task_lists(mock_db, mock_user):
    mock_task_list = MagicMock(id=1, name="List X", owner_id=mock_user.id)
    # Configurar valores reales
    mock_task_list.id = 1
    mock_task_list.name = "List X"
    mock_task_list.description = "Test description"
    mock_task_list.owner_id = mock_user.id
    mock_task_list.created_at = datetime.now()
    mock_task_list.updated_at = datetime.now()

    mock_db.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.all.return_value = [
        (mock_task_list, 5, 3)
    ]
    result = task_lists.get_task_lists(mock_db, mock_user)
    assert result[0].task_count == 5


def test_get_task_list_success(mock_db, mock_user):
    mock_task_list = MagicMock(id=1, name="List X", owner_id=mock_user.id)
    # Configurar valores reales
    mock_task_list.id = 1
    mock_task_list.name = "List X"
    mock_task_list.description = "Test description"
    mock_task_list.owner_id = mock_user.id
    mock_task_list.created_at = datetime.now()
    mock_task_list.updated_at = datetime.now()

    mock_db.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.first.return_value = (
        mock_task_list,
        5,
        2,
    )
    result = task_lists.get_task_list(1, mock_db, mock_user)
    assert result.id == 1


def test_get_task_list_not_found(mock_db, mock_user):
    mock_db.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.first.return_value = (
        None
    )
    with pytest.raises(HTTPException):
        task_lists.get_task_list(1, mock_db, mock_user)


def test_delete_task_list_success(mock_db, mock_user):
    mock_task_list = MagicMock(name="List X")
    mock_task_list.name = "List X"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_task_list

    result = task_lists.delete_task_list(1, mock_db, mock_user)
    assert "deleted successfully" in result["message"]


def test_delete_task_list_not_found(mock_db, mock_user):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException):
        task_lists.delete_task_list(1, mock_db, mock_user)


def test_update_task_list_success(mock_db, mock_user):
    mock_task_list = MagicMock(id=1, name="Old List", owner_id=mock_user.id)
    # Configurar valores reales
    mock_task_list.id = 1
    mock_task_list.name = "Old List"
    mock_task_list.description = "Old description"
    mock_task_list.owner_id = mock_user.id
    mock_task_list.created_at = datetime.now()
    mock_task_list.updated_at = datetime.now()

    mock_db.query.return_value.filter.return_value.first.return_value = mock_task_list
    mock_db.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.first.return_value = (
        mock_task_list,
        3,
        1,
    )

    dto = TaskListUpdateDTO(name="Updated List")
    result = task_lists.update_task_list(1, dto, mock_db, mock_user)
    assert result.name == "Updated List"


def test_update_task_list_not_found(mock_db, mock_user):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException):
        task_lists.update_task_list(1, TaskListUpdateDTO(name="X"), mock_db, mock_user)
