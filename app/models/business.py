from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Business(SQLModel, table=True):
    __tablename__ = "business"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    store_code: str = Field(index=True, unique=True)
    currency: str = Field(default="NGN")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
