from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    __tablename__ = "customer"
    __table_args__ = (
        UniqueConstraint("business_id", "channel_type", "channel_user_id", name="uq_customer_business_channel_user"),
    )

    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id", index=True)
    channel_type: str = Field(index=True)
    channel_user_id: str = Field(index=True)
    display_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
