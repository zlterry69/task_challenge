from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_app_creation():
    from src.presentation.main import app

    assert isinstance(app, FastAPI)
    assert app.title == "Task Challenge API"


def test_ping_endpoint():
    from src.presentation.main import app

    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_openapi_docs():
    from src.presentation.main import app

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
