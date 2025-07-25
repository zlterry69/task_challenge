from functools import lru_cache
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.application.auth_service import get_current_user
from src.application.services import NotificationService, TaskListService, TaskService
from src.infrastructure.database import SessionLocal, UserModel, get_db_session

# Bearer token scheme (simpler than OAuth2)
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def get_task_list_service(db: Session = Depends(get_db_session)) -> TaskListService:
    return TaskListService(db)


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


@lru_cache()
def get_notification_service() -> NotificationService:
    return NotificationService()


class GraphQLDependencies:
    @staticmethod
    def get_db() -> Session:
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()

    @staticmethod
    def get_current_user_from_context(info) -> UserModel:
        return None
