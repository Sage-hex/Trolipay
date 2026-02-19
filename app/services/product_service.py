from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlmodel import Session

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.models.product import Product
from app.repositories.product_repo import create_product, get_product_by_id, list_active_products, save_product
from app.services.money import naira_to_kobo


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def create_product_service(
    session: Session,
    business_id: int,
    name: str,
    description: str | None,
    base_price_naira: int,
    image_url: str | None,
) -> Product:
    base_price_kobo = naira_to_kobo(base_price_naira)
    return create_product(
        session,
        business_id=business_id,
        name=name,
        description=description,
        base_price_kobo=base_price_kobo,
        image_url=image_url,
    )


def list_products_service(session: Session, business_id: int) -> list[Product]:
    return list_active_products(session, business_id=business_id)


def update_product_service(
    session: Session,
    business_id: int,
    product_id: int,
    name: str | None,
    description: str | None,
    base_price_naira: int | None,
    image_url: str | None,
) -> Product:
    product = get_product_by_id(session, business_id=business_id, product_id=product_id)
    if not product or not product.is_active:
        raise NotFoundError(message="Product not found")

    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if base_price_naira is not None:
        product.base_price_kobo = naira_to_kobo(base_price_naira)
    if image_url is not None:
        product.image_url = image_url

    return save_product(session, product)


def soft_delete_product_service(session: Session, business_id: int, product_id: int) -> None:
    product = get_product_by_id(session, business_id=business_id, product_id=product_id)
    if not product:
        raise NotFoundError(message="Product not found")

    product.is_active = False
    save_product(session, product)


def upload_product_image_service(file: UploadFile) -> str:
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValidationError(message="Unsupported image type")

    filename = f"{uuid4().hex}{suffix}"
    media_products = Path(settings.media_dir) / "products"
    media_products.mkdir(parents=True, exist_ok=True)
    destination = media_products / filename

    with destination.open("wb") as output:
        output.write(file.file.read())

    return f"/media/products/{filename}"
