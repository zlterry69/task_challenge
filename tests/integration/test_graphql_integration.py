from fastapi.testclient import TestClient

from src.presentation.main import app

client = TestClient(app)


def test_graphql_endpoint_exists():
    """Test that GraphQL endpoint exists"""
    response = client.get("/graphql")
    assert response.status_code == 200


def test_graphql_user_registration():
    """Test GraphQL user registration"""
    # GraphQL mutation
    mutation = """
    mutation RegisterUser($input: UserCreateInput!) {
        register(input: $input) {
            accessToken
            tokenType
            user {
                id
                email
                fullName
            }
        }
    }
    """

    variables = {
        "input": {
            "email": "graphql@example.com",
            "fullName": "GraphQL User",
            "password": "password123",
        }
    }

    response = client.post("/graphql", json={"query": mutation, "variables": variables})

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    # Note: This will only work if the GraphQL endpoint and schema are properly configured


def test_graphql_task_list_operations():
    """Test GraphQL task list operations"""
    # First register and get token
    client.post(
        "/api/auth/register",
        json={
            "email": "graphql_tasks@example.com",
            "full_name": "GraphQL Tasks User",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/api/auth/login",
        data={"username": "graphql_tasks@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # GraphQL mutation to create task list
    mutation = """
    mutation CreateTaskList($input: TaskListCreateInput!) {
        createTaskList(input: $input) {
            id
            name
            description
            ownerId
        }
    }
    """

    variables = {
        "input": {"name": "GraphQL List", "description": "Created via GraphQL"}
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/graphql", json={"query": mutation, "variables": variables}, headers=headers
    )

    assert response.status_code == 200


def test_graphql_error_handling():
    """Test GraphQL error handling"""
    # Test with invalid query
    response = client.post("/graphql", json={"query": "invalid query {"})

    assert response.status_code == 200
    data = response.json()
    assert "errors" in data
