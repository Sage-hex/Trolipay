from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlmodel")
pytest.importorskip("jose")
pytest.importorskip("passlib")
pytest.importorskip("sqlalchemy")

from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.auth import get_current_business_id
from app.core.db import get_session
from app.main import app
from app.models.business import Business


def _test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _seed_business(engine, business_id: int, name: str, store_code: str) -> None:
    with Session(engine) as session:
        session.add(Business(id=business_id, name=name, store_code=store_code))
        session.commit()


def test_products_crud_and_soft_delete() -> None:
    engine = _test_engine()
    _seed_business(engine, business_id=1, name="Biz One", store_code="BIZ1")

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_business_id] = lambda: 1

    with TestClient(app) as client:
        create_res = client.post(
            "/api/v1/products",
            json={"name": "Cake", "description": "Chocolate", "base_price_naira": 18000},
        )
        assert create_res.status_code == 200
        product = create_res.json()
        assert product["base_price_kobo"] == 1800000
        product_id = product["id"]

        list_res = client.get("/api/v1/products")
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1

        patch_res = client.patch(
            f"/api/v1/products/{product_id}",
            json={"name": "Cake XL", "base_price_naira": 20000},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["name"] == "Cake XL"
        assert patch_res.json()["base_price_kobo"] == 2000000

        delete_res = client.delete(f"/api/v1/products/{product_id}")
        assert delete_res.status_code == 200
        assert delete_res.json() == {"ok": True}

        list_after_delete = client.get("/api/v1/products")
        assert list_after_delete.status_code == 200
        assert list_after_delete.json() == []

    app.dependency_overrides.clear()


def test_products_tenant_scoping() -> None:
    engine = _test_engine()
    _seed_business(engine, business_id=1, name="Biz One", store_code="BIZ1")
    _seed_business(engine, business_id=2, name="Biz Two", store_code="BIZ2")

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        app.dependency_overrides[get_current_business_id] = lambda: 1
        create_res = client.post("/api/v1/products", json={"name": "Cake", "base_price_naira": 1000})
        product_id = create_res.json()["id"]

        app.dependency_overrides[get_current_business_id] = lambda: 2
        other_tenant_get = client.patch(f"/api/v1/products/{product_id}", json={"name": "No Access"})
        assert other_tenant_get.status_code == 404

        other_tenant_list = client.get("/api/v1/products")
        assert other_tenant_list.status_code == 200
        assert other_tenant_list.json() == []

    app.dependency_overrides.clear()


def test_upload_product_image_returns_url_and_saves_file() -> None:
    app.dependency_overrides[get_current_business_id] = lambda: 1

    with TestClient(app) as client:
        files = {"file": ("product.png", b"fake-png-binary", "image/png")}
        response = client.post("/api/v1/uploads/product-image", files=files)
        assert response.status_code == 200
        image_url = response.json()["image_url"]
        assert image_url.startswith("/media/products/")

        filename = image_url.rsplit("/", maxsplit=1)[1]
        file_path = Path("media") / "products" / filename
        assert file_path.exists()
        file_path.unlink(missing_ok=True)
