from sqlmodel import Field, SQLModel


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_item"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    product_id: int | None = Field(default=None, foreign_key="product.id")
    name_snapshot: str
    unit_price_kobo: int
    quantity: int
    line_total_kobo: int
