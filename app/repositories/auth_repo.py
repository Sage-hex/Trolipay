from sqlmodel import Session, select

from app.models.business import Business
from app.models.user import User


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()


def get_business_by_id(session: Session, business_id: int) -> Business | None:
    statement = select(Business).where(Business.id == business_id)
    return session.exec(statement).first()


def create_business(session: Session, name: str, store_code: str) -> Business:
    business = Business(name=name, store_code=store_code)
    session.add(business)
    session.flush()
    session.refresh(business)
    return business


def create_owner_user(session: Session, business_id: int, email: str, password_hash: str) -> User:
    user = User(business_id=business_id, email=email, password_hash=password_hash, role="owner")
    session.add(user)
    session.flush()
    session.refresh(user)
    return user
