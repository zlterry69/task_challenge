from typing import Optional

from strawberry.types import Info

from src.infrastructure.auth import decode_access_token
from src.infrastructure.database import SessionLocal, UserModel


def get_db():
    """Get database session - reusing REST logic"""
    return SessionLocal()


def get_current_user_from_context(info: Info) -> Optional[UserModel]:
    if not hasattr(info.context, "get"):
        return None

    token = info.context.get("token")
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None

        db = SessionLocal()
        user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
        db.close()
        return user
    except Exception as e:
        print(f"⚠️ Error decoding token in context: {e}")
        return None


def require_auth(info):
    headers = info.context["request"].headers
    token = headers.get("authorization", "").replace("Bearer ", "")

    payload = decode_access_token(token)
    user_id = payload.get("sub")

    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        return user
    finally:
        db.close()
