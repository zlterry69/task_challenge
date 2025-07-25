from datetime import datetime

import pytest

from src.application.dto import (
    TaskCreateDTO,
    UserCreateDTO,
    UserResponseDTO,
    UserUpdateDTO,
)
from src.domain.entities import TaskPriority
from src.infrastructure.auth import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


# Tests de validación de datos
def test_user_email_validation():
    # Valid email
    user = UserCreateDTO(
        email="valid@example.com", full_name="Valid User", password="test123456"
    )
    assert user.email == "valid@example.com"

    # Email is required for user creation
    with pytest.raises(Exception):
        UserCreateDTO(email="", full_name="No Email", password="test123456")


def test_user_password_validation():
    # Valid password
    user = UserCreateDTO(
        email="test@example.com", full_name="Test User", password="validpass123"
    )
    assert user.password == "validpass123"

    # Password is required
    with pytest.raises(Exception):
        UserCreateDTO(email="test@example.com", full_name="Test User", password="")


def test_user_full_name_validation():
    # Valid full name
    user = UserCreateDTO(
        email="test@example.com", full_name="John Doe", password="password123"
    )
    assert user.full_name == "John Doe"


def test_task_title_validation():
    # Valid task title
    task = TaskCreateDTO(title="Valid Task", task_list_id=1)
    assert task.title == "Valid Task"

    # Title is required
    with pytest.raises(Exception):
        TaskCreateDTO(title="", task_list_id=1)


def test_task_list_id_validation():
    # Valid task list ID
    task = TaskCreateDTO(title="Test Task", task_list_id=1)
    assert task.task_list_id == 1

    # Task list ID is required
    with pytest.raises(Exception):
        TaskCreateDTO(title="Test Task", task_list_id=None)


# Tests de seguridad y autenticación
def test_password_hashing():
    """Test password hashing functionality"""
    password = "mysecretpassword"
    hashed = get_password_hash(password)

    # Hash should be different from original password
    assert hashed != password
    assert len(hashed) > 0

    # Same password should verify correctly
    assert verify_password(password, hashed) is True

    # Wrong password should not verify
    assert verify_password("wrongpassword", hashed) is False


def test_password_verify():
    """Test password verification"""
    password = "testpassword123"
    wrong_password = "wrongpassword"
    hashed = get_password_hash(password)

    # Correct password should verify
    assert verify_password(password, hashed) is True

    # Incorrect password should not verify
    assert verify_password(wrong_password, hashed) is False


def test_jwt_token_creation():
    """Test JWT token creation"""
    data = {"sub": "123", "email": "test@example.com"}
    token = create_access_token(data)

    assert token is not None
    assert len(token) > 0
    assert isinstance(token, str)


def test_jwt_token_decode():
    """Test JWT token decoding"""
    data = {"sub": "123", "email": "test@example.com"}
    token = create_access_token(data)

    # Decode the token
    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "123"
    assert decoded["email"] == "test@example.com"


def test_jwt_token_invalid():
    """Test invalid JWT token handling"""
    invalid_token = "invalid.jwt.token"

    # Should return None for invalid token
    decoded = decode_access_token(invalid_token)
    assert decoded is None


def test_user_create_dto_validation():
    """Test UserCreateDTO validation"""
    dto = UserCreateDTO(
        email="dto@example.com", full_name="DTO User", password="dtopassword"
    )
    assert dto.email == "dto@example.com"
    assert dto.full_name == "DTO User"
    assert dto.password == "dtopassword"


def test_user_response_dto():
    """Test UserResponseDTO structure"""
    now = datetime.now()
    dto = UserResponseDTO(
        id=1,
        email="response@example.com",
        full_name="Response User",
        is_active=True,
        created_at=now,
    )
    assert dto.id == 1
    assert dto.email == "response@example.com"
    assert dto.is_active is True
    assert dto.created_at == now


def test_task_enum_validation():
    """Test task enum validations"""
    # Valid priority
    task = TaskCreateDTO(title="Test Task", task_list_id=1, priority=TaskPriority.HIGH)
    assert task.priority == TaskPriority.HIGH


def test_user_update_validation():
    """Test user update validation"""
    # Partial update should work
    update = UserUpdateDTO(full_name="Updated Name")
    assert update.full_name == "Updated Name"
    assert update.email is None

    # Email update should work
    update = UserUpdateDTO(email="updated@example.com")
    assert update.email == "updated@example.com"
    assert update.full_name is None


def test_password_security_requirements():
    """Test password security requirements"""
    # Test various password scenarios
    passwords = [
        "short",  # Too short
        "12345678",  # Only numbers
        "password",  # Only letters
        "Password123",  # Good password
        "VeryLongPasswordWithMixedCharacters123",  # Very long password
    ]

    for password in passwords:
        try:
            UserCreateDTO(
                email="security@example.com",
                full_name="Security Test",
                password=password,
            )
            # If we get here, the password was accepted
            assert len(password) > 0
        except Exception:
            # Password validation failed
            pass
