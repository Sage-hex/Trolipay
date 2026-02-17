from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.errors import AuthError, ConflictError
from app.core.security import hash_password, verify_password
from app.models.business import Business
from app.models.user import User
from app.repositories.auth_repo import (
    create_business,
    create_owner_user,
    get_business_by_id,
    get_user_by_email,
    get_user_by_id,
)


def register_business_owner(
    session: Session,
    business_name: str,
    store_code: str,
    email: str,
    password: str,
) -> tuple[User, Business]:
    try:
        with session.begin():
            business = create_business(session, name=business_name, store_code=store_code)
            user = create_owner_user(
                session,
                business_id=business.id,
                email=email,
                password_hash=hash_password(password),
            )
    except IntegrityError as exc:
        session.rollback()
        raise ConflictError(message="Store code or email already exists") from exc

    return user, business


def authenticate_user(session: Session, email: str, password: str) -> User:
    user = get_user_by_email(session, email=email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthError(message="Invalid email or password")
    return user


def get_user_with_business(session: Session, user_id: int) -> tuple[User, Business]:
    user = get_user_by_id(session, user_id=user_id)
    if not user:
        raise AuthError(message="Invalid authentication credentials")

    business = get_business_by_id(session, business_id=user.business_id)
    if not business:
        raise AuthError(message="Invalid authentication credentials")

    return user, business
