from sqlmodel import Session

from app.core.errors import NotFoundError, ValidationError
from app.models.business import Business
from app.repositories.business_repo import get_business_by_id, update_business_name


def get_business(session: Session, business_id: int) -> Business:
    business = get_business_by_id(session, business_id=business_id)
    if not business:
        raise NotFoundError(message="Business not found")
    return business


def patch_business(session: Session, business_id: int, name: str | None, store_code: str | None) -> Business:
    if store_code is not None:
        raise ValidationError(message="store_code cannot be updated")
    if name is None:
        raise ValidationError(message="name is required")

    business = update_business_name(session, business_id=business_id, name=name)
    if not business:
        raise NotFoundError(message="Business not found")
    return business
