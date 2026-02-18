from sqlmodel import Session, select

from app.models.delivery_zone import DeliveryZone


def create_delivery_zone(session: Session, business_id: int, name: str, fee_kobo: int) -> DeliveryZone:
    zone = DeliveryZone(business_id=business_id, name=name, fee_kobo=fee_kobo, is_active=True)
    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone


def list_active_delivery_zones(session: Session, business_id: int) -> list[DeliveryZone]:
    statement = (
        select(DeliveryZone)
        .where(DeliveryZone.business_id == business_id)
        .where(DeliveryZone.is_active.is_(True))
        .order_by(DeliveryZone.id.desc())
    )
    return list(session.exec(statement).all())


def get_delivery_zone_by_id(session: Session, business_id: int, zone_id: int) -> DeliveryZone | None:
    statement = (
        select(DeliveryZone)
        .where(DeliveryZone.id == zone_id)
        .where(DeliveryZone.business_id == business_id)
    )
    return session.exec(statement).first()


def save_delivery_zone(session: Session, zone: DeliveryZone) -> DeliveryZone:
    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone
