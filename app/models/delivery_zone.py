from sqlmodel import Field, SQLModel


class DeliveryZone(SQLModel, table=True):
    __tablename__ = "delivery_zone"

    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id", index=True)
    name: str
    fee_kobo: int
    is_active: bool = Field(default=True)
