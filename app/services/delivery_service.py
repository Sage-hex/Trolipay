from sqlmodel import Session

from app.core.errors import NotFoundError
from app.models.delivery_zone import DeliveryZone
from app.repositories.delivery_repo import (
    create_delivery_zone,
    get_delivery_zone_by_id,
    list_active_delivery_zones,
    save_delivery_zone,
)
from app.services.money import naira_to_kobo


def create_delivery_zone_service(session: Session, business_id: int, name: str, fee_naira: int) -> DeliveryZone:
    fee_kobo = naira_to_kobo(fee_naira)
    return create_delivery_zone(session, business_id=business_id, name=name, fee_kobo=fee_kobo)


def list_delivery_zones_service(session: Session, business_id: int) -> list[DeliveryZone]:
    return list_active_delivery_zones(session, business_id=business_id)


def update_delivery_zone_service(
    session: Session,
    business_id: int,
    zone_id: int,
    name: str | None,
    fee_naira: int | None,
) -> DeliveryZone:
    zone = get_delivery_zone_by_id(session, business_id=business_id, zone_id=zone_id)
    if not zone or not zone.is_active:
        raise NotFoundError(message="Delivery zone not found")

    if name is not None:
        zone.name = name
    if fee_naira is not None:
        zone.fee_kobo = naira_to_kobo(fee_naira)

    return save_delivery_zone(session, zone)


def soft_delete_delivery_zone_service(session: Session, business_id: int, zone_id: int) -> None:
    zone = get_delivery_zone_by_id(session, business_id=business_id, zone_id=zone_id)
    if not zone:
        raise NotFoundError(message="Delivery zone not found")

    zone.is_active = False
    save_delivery_zone(session, zone)
