from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.auth import get_current_business_id
from app.core.db import get_session
from app.services.business_service import get_business, patch_business

router = APIRouter(tags=["business"])


class BusinessResponse(BaseModel):
    id: int
    name: str
    store_code: str
    currency: str


class BusinessPatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    store_code: str | None = None


@router.get("/business", response_model=BusinessResponse)
def get_business_endpoint(
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> BusinessResponse:
    business = get_business(session, business_id=business_id)
    return BusinessResponse(
        id=business.id,
        name=business.name,
        store_code=business.store_code,
        currency=business.currency,
    )


@router.patch("/business", response_model=BusinessResponse)
def patch_business_endpoint(
    payload: BusinessPatchRequest,
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> BusinessResponse:
    business = patch_business(
        session,
        business_id=business_id,
        name=payload.name,
        store_code=payload.store_code,
    )
    return BusinessResponse(
        id=business.id,
        name=business.name,
        store_code=business.store_code,
        currency=business.currency,
    )
