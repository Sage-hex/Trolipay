from sqlmodel import Session, select

from app.models.product import Product


def create_product(
    session: Session,
    business_id: int,
    name: str,
    description: str | None,
    base_price_kobo: int,
    image_url: str | None,
) -> Product:
    product = Product(
        business_id=business_id,
        name=name,
        description=description,
        base_price_kobo=base_price_kobo,
        image_url=image_url,
        is_active=True,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def list_active_products(session: Session, business_id: int) -> list[Product]:
    statement = (
        select(Product)
        .where(Product.business_id == business_id)
        .where(Product.is_active.is_(True))
        .order_by(Product.id.desc())
    )
    return list(session.exec(statement).all())


def get_product_by_id(session: Session, business_id: int, product_id: int) -> Product | None:
    statement = (
        select(Product)
        .where(Product.id == product_id)
        .where(Product.business_id == business_id)
    )
    return session.exec(statement).first()


def save_product(session: Session, product: Product) -> Product:
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
