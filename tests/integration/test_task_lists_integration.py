from fastapi.testclient import TestClient

from src.presentation.main import app

client = TestClient(app)


def test_task_list_crud(clean_database):
    """Test task list CRUD operations with real database"""
    # First register and get token
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "tasklist@example.com",
            "full_name": "TaskList User",
            "password": "password123",
        },
    )
    assert register_response.status_code == 200  # Registration devuelve 200, no 201

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "tasklist@example.com",  # username, no email
            "password": "password123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test create task list
    task_list_data = {"name": "Test List", "description": "Test Description"}

    response = client.post("/api/task-lists/", json=task_list_data, headers=headers)
    assert response.status_code == 200  # Task lists también devuelven 200, no 201

    data = response.json()
    assert data["name"] == "Test List"
    assert data["description"] == "Test Description"
    task_list_id = data["id"]

    # Test get task lists
    response = client.get("/api/task-lists/", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test List"

    # Test get task list by ID
    response = client.get(f"/api/task-lists/{task_list_id}", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_list_id
    assert data["name"] == "Test List"

    # Test update task list
    update_data = {"name": "Updated List", "description": "Updated Description"}

    response = client.put(
        f"/api/task-lists/{task_list_id}", json=update_data, headers=headers
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated List"
    assert data["description"] == "Updated Description"

    # Test delete task list
    response = client.delete(f"/api/task-lists/{task_list_id}", headers=headers)
    assert response.status_code == 200
