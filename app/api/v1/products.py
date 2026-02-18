from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.auth import get_current_business_id
from app.core.db import get_session
from app.services.product_service import (
    create_product_service,
    list_products_service,
    soft_delete_product_service,
    update_product_service,
    upload_product_image_service,
)

router = APIRouter(tags=["products"])


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    base_price_naira: int = Field(ge=0)
    image_url: str | None = None


class ProductPatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    base_price_naira: int | None = Field(default=None, ge=0)
    image_url: str | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    base_price_kobo: int
    image_url: str | None
    is_active: bool


class ProductImageUploadResponse(BaseModel):
    image_url: str


def _to_response(product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        base_price_kobo=product.base_price_kobo,
        image_url=product.image_url,
        is_active=product.is_active,
    )


@router.post("/products", response_model=ProductResponse)
def create_product_endpoint(
    payload: ProductCreateRequest,
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> ProductResponse:
    product = create_product_service(
        session,
        business_id=business_id,
        name=payload.name,
        description=payload.description,
        base_price_naira=payload.base_price_naira,
        image_url=payload.image_url,
    )
    return _to_response(product)


@router.get("/products", response_model=list[ProductResponse])
def list_products_endpoint(
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> list[ProductResponse]:
    products = list_products_service(session, business_id=business_id)
    return [_to_response(product) for product in products]


@router.patch("/products/{product_id}", response_model=ProductResponse)
def patch_product_endpoint(
    product_id: int,
    payload: ProductPatchRequest,
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> ProductResponse:
    product = update_product_service(
        session,
        business_id=business_id,
        product_id=product_id,
        name=payload.name,
        description=payload.description,
        base_price_naira=payload.base_price_naira,
        image_url=payload.image_url,
    )
    return _to_response(product)


@router.delete("/products/{product_id}")
def delete_product_endpoint(
    product_id: int,
    session: Session = Depends(get_session),
    business_id: int = Depends(get_current_business_id),
) -> dict[str, bool]:
    soft_delete_product_service(session, business_id=business_id, product_id=product_id)
    return {"ok": True}


@router.post("/uploads/product-image", response_model=ProductImageUploadResponse)
def upload_product_image_endpoint(
    file: UploadFile,
    _business_id: int = Depends(get_current_business_id),
) -> ProductImageUploadResponse:
    image_url = upload_product_image_service(file)
    return ProductImageUploadResponse(image_url=image_url)
