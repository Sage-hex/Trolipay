from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    provider: str = Field(default="paystack")
    status: str = Field(default="initiated", index=True)
    amount_kobo: int
    currency: str = Field(default="NGN")
    paystack_reference: str | None = Field(default=None, index=True, unique=True)
    authorization_url: str | None = None
    raw_event_json: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confirmed_at: datetime | None = None
