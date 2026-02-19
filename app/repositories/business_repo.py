from sqlmodel import Session, select

from app.models.business import Business


def get_business_by_id(session: Session, business_id: int) -> Business | None:
    statement = select(Business).where(Business.id == business_id)
    return session.exec(statement).first()


def update_business_name(session: Session, business_id: int, name: str) -> Business | None:
    business = get_business_by_id(session, business_id=business_id)
    if not business:
        return None

    business.name = name
    session.add(business)
    session.commit()
    session.refresh(business)
    return business
