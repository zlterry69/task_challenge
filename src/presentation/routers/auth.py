from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.application.auth_service import (
    get_current_user,
    login_for_access_token,
    register_user,
)
from src.application.dto import UserCreateDTO, UserResponseDTO
from src.infrastructure.database import SessionLocal, UserModel

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserResponseDTO)
def register(user_in: UserCreateDTO, db: Session = Depends(get_db)):
    user = register_user(db, user_in)
    return UserResponseDTO(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return login_for_access_token(db, form_data.username, form_data.password)


@router.get("/me", response_model=UserResponseDTO)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return UserResponseDTO(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
