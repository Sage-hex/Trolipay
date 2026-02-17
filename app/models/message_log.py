from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class MessageLog(SQLModel, table=True):
    __tablename__ = "message_log"

    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id", index=True)
    customer_id: int | None = Field(default=None, foreign_key="customer.id")
    channel_type: str
    direction: str
    text: str | None = None
    status: str = Field(default="sent")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
