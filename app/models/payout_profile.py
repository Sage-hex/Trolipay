from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class PayoutProfile(SQLModel, table=True):
    __tablename__ = "payout_profile"

    business_id: int = Field(foreign_key="business.id", primary_key=True, unique=True)
    bank_name: str
    account_number: str
    account_name: str
    paystack_subaccount_code: str | None = None
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
