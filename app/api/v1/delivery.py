from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.auth import get_current_business_id
from app.core.db import get_session
from app.services.delivery_service import (
    create_delivery_zone_service,
    list_delivery_zones_service,
    soft_delete_delivery_zone_service,
    update_delivery_zone_service,
)

router = APIRouter(tags=["delivery-zones"])


class DeliveryZoneCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    fee_naira: int = Field(ge=0)


class DeliveryZonePatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    fee_naira: int | None = Field(default=None, ge=0)


class DeliveryZoneResponse(BaseModel):
    id: int
    name: str
    fee_kobo: int
    is_active: bool


def _to_response(zone) -> DeliveryZoneResponse:
    return DeliveryZoneResponse(
        id=zone.id,
        name=zone.name,
        fee_kobo=zone.fee_kobo,
        is_active=zone.is_active,
    )


@router.post("/delivery-zones", response_model=DeliveryZoneResponse)
def create_delivery_zone_endpoint(
    payload: DeliveryZoneCreateRequest,
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> DeliveryZoneResponse:
    zone = create_delivery_zone_service(session, business_id=business_id, name=payload.name, fee_naira=payload.fee_naira)
    return _to_response(zone)


@router.get("/delivery-zones", response_model=list[DeliveryZoneResponse])
def list_delivery_zones_endpoint(
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> list[DeliveryZoneResponse]:
    zones = list_delivery_zones_service(session, business_id=business_id)
    return [_to_response(zone) for zone in zones]


@router.patch("/delivery-zones/{zone_id}", response_model=DeliveryZoneResponse)
def patch_delivery_zone_endpoint(
    zone_id: int,
    payload: DeliveryZonePatchRequest,
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> DeliveryZoneResponse:
    zone = update_delivery_zone_service(
        session,
        business_id=business_id,
        zone_id=zone_id,
        name=payload.name,
        fee_naira=payload.fee_naira,
    )
    return _to_response(zone)


@router.delete("/delivery-zones/{zone_id}")
def delete_delivery_zone_endpoint(
    zone_id: int,
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> dict[str, bool]:
    soft_delete_delivery_zone_service(session, business_id=business_id, zone_id=zone_id)
    return {"ok": True}
