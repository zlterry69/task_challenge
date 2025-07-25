from typing import Optional

from strawberry.types import Info

from src.application.auth_service import get_current_user
from src.infrastructure.database import SessionLocal, UserModel


def get_db():
    """Get database session - reusing REST logic"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def get_current_user_from_context(info: Info) -> Optional[UserModel]:
    """Get current user from context"""
    if hasattr(info.context, "get") and info.context.get("user"):
        return info.context["user"]

    # Temporalmente deshabilitado hasta arreglar el context
    # TODO: Implementar autenticación GraphQL correctamente
    return None


def require_auth(info: Info) -> UserModel:
    """
    Require authentication - raises exception if not authenticated
    GraphQL best practice for protected resolvers
    """
    user = get_current_user_from_context(info)
    if not user:
        raise Exception("Authentication required. Please provide a valid Bearer token.")
    return user
