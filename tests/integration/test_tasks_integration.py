from fastapi.testclient import TestClient

from src.presentation.main import app

client = TestClient(app)


def test_task_crud(clean_database):
    """Test task CRUD operations with real database"""
    # First register and get token
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "tasks@example.com",
            "full_name": "Tasks User",
            "password": "password123",
        },
    )
    assert register_response.status_code == 200  # Registration devuelve 200, no 201

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "tasks@example.com",  # username, no email
            "password": "password123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a task list first
    task_list_data = {"name": "Test List for Tasks", "description": "Test Description"}

    response = client.post("/api/task-lists/", json=task_list_data, headers=headers)
    assert response.status_code == 200  # Task lists devuelven 200, no 201
    task_list_id = response.json()["id"]

    # Test create task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "task_list_id": task_list_id,
        "priority": "medium",
    }

    response = client.post("/api/tasks/", json=task_data, headers=headers)
    assert response.status_code == 200  # Tasks también devuelven 200, no 201

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    task_id = data["id"]

    # Test get tasks
    response = client.get("/api/tasks/", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1

    # Verify the created task is in the list
    created_task = None
    for task in data:
        if task["title"] == "Test Task":
            created_task = task
            break

    assert created_task is not None
    assert created_task["description"] == "Test Description"
    task_id = created_task["id"]

    # Test update task (using the task_id from the list)
    update_data = {"title": "Updated Task", "description": "Updated Description"}

    response = client.put(f"/api/tasks/{task_id}", json=update_data, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated Description"

    # Test delete task
    response = client.delete(f"/api/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
