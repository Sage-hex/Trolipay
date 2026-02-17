from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Receipt(SQLModel, table=True):
    __tablename__ = "receipt"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    receipt_number: str = Field(index=True)
    pdf_url: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
