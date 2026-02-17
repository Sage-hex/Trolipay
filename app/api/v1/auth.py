from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session

from app.core.auth import get_current_user
from app.core.db import get_session
from app.core.security import create_access_token
from app.models.user import User
from app.services.auth_service import authenticate_user, get_user_with_business, register_business_owner

router = APIRouter(tags=["auth"])


class RegisterRequest(BaseModel):
    business_name: str = Field(min_length=1)
    store_code: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    user: dict
    business: dict


@router.post("/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user, _business = register_business_owner(
        session,
        business_name=payload.business_name,
        store_code=payload.store_code,
        email=payload.email,
        password=payload.password,
    )
    token = create_access_token(user_id=user.id, business_id=user.business_id)
    return TokenResponse(access_token=token)


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = authenticate_user(session, email=payload.email, password=payload.password)
    token = create_access_token(user_id=user.id, business_id=user.business_id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(current_user: Annotated[User, Depends(get_current_user)], session: Session = Depends(get_session)) -> MeResponse:
    user, business = get_user_with_business(session, user_id=current_user.id)
    return MeResponse(
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "business_id": user.business_id,
        },
        business={
            "id": business.id,
            "name": business.name,
            "store_code": business.store_code,
            "currency": business.currency,
        },
    )
