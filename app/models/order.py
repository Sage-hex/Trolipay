from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    __tablename__ = "order"

    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id", index=True)
    customer_id: int = Field(foreign_key="customer.id", index=True)
    channel_type: str = Field(index=True)
    status: str = Field(default="reserved", index=True)
    subtotal_kobo: int
    delivery_fee_kobo: int
    total_kobo: int
    platform_fee_kobo: int
    business_payout_kobo: int
    delivery_zone_id: int | None = Field(default=None, foreign_key="delivery_zone.id")
    delivery_address: str | None = None
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
