from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"

    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id", index=True)
    customer_id: int = Field(foreign_key="customer.id", index=True)
    channel_type: str = Field(index=True)
    channel_thread_id: str = Field(index=True)
    current_state: str = Field(default="idle")
    last_message_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
