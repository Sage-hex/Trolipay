from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.db import get_session
from app.core.errors import AuthError
from app.core.security import decode_access_token
from app.models.user import User
from app.services.auth_service import get_user_with_business

bearer_scheme = HTTPBearer(auto_error=False)


SessionDep = Annotated[Session, Depends(get_session)]
BearerDep = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


def get_current_user(session: SessionDep, credentials: BearerDep) -> User:
    if credentials is None:
        raise AuthError(message="Authentication required")

    payload = decode_access_token(credentials.credentials)
    user, _ = get_user_with_business(session, user_id=int(payload["user_id"]))
    return user


def get_current_business_id(current_user: Annotated[User, Depends(get_current_user)]) -> int:
    return current_user.business_id
