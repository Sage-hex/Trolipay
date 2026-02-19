from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id", index=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="owner")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
