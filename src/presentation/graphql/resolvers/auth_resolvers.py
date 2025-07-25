import strawberry
from strawberry.types import Info

from src.application.auth_service import login_for_access_token, register_user
from src.application.dto import UserCreateDTO

from ..context import get_db, require_auth
from ..types import AuthPayload, User, UserCreateInput, UserLoginInput


@strawberry.type
class AuthQuery:
    @strawberry.field
    def me(self, info: Info) -> User:
        """Get current authenticated user - requires Bearer token"""
        user = require_auth(info)
        return User(id=user.id, email=user.email, full_name=user.full_name)


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    def register(self, input: UserCreateInput) -> User:
        """Register new user - reuses REST logic"""
        db = get_db()
        try:
            # Validate input
            if not input.email:
                raise Exception("Email is required")
            if not input.password:
                raise Exception("Password is required")
            if len(input.password) < 8:
                raise Exception("Password must be at least 8 characters long")

            user_create = UserCreateDTO(
                email=input.email, full_name=input.full_name, password=input.password
            )
            user = register_user(db, user_create)
            return User(id=user.id, email=user.email, full_name=user.full_name)
        except ValueError as e:
            raise Exception(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Registration failed: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def login(self, login_input: UserLoginInput) -> AuthPayload:
        """Login user - reuses REST logic"""
        from src.infrastructure.database import UserModel

        db = get_db()
        try:
            auth_result = login_for_access_token(
                db, login_input.email, login_input.password
            )

            user = (
                db.query(UserModel).filter(UserModel.email == login_input.email).first()
            )

            return AuthPayload(
                access_token=auth_result["access_token"],
                token_type=auth_result["token_type"],
                user=User(id=user.id, email=user.email, full_name=user.full_name),
            )
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
        finally:
            db.close()
