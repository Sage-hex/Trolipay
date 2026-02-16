from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    __tablename__ = "product"

    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id", index=True)
    name: str = Field(index=True)
    description: str | None = None
    base_price_kobo: int
    image_url: str | None = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
