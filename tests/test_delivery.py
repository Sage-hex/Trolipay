import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlmodel")
pytest.importorskip("jose")
pytest.importorskip("passlib")
pytest.importorskip("sqlalchemy")

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.auth import get_current_business_id
from app.core.db import get_session
from app.main import app
from tests.db_test_utils import create_test_engine
from app.models.business import Business


def _test_engine():
    return create_test_engine()


def _seed_business(engine, business_id: int, name: str, store_code: str) -> None:
    with Session(engine) as session:
        session.add(Business(id=business_id, name=name, store_code=store_code))
        session.commit()


def test_delivery_zones_crud_and_soft_delete() -> None:
    engine = _test_engine()
    _seed_business(engine, business_id=1, name="Biz One", store_code="BIZ1")

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_business_id] = lambda: 1

    with TestClient(app) as client:
        create_res = client.post("/api/v1/delivery-zones", json={"name": "Island", "fee_naira": 2500})
        assert create_res.status_code == 200
        zone = create_res.json()
        assert zone["fee_kobo"] == 250000
        zone_id = zone["id"]

        list_res = client.get("/api/v1/delivery-zones")
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1

        patch_res = client.patch(f"/api/v1/delivery-zones/{zone_id}", json={"name": "Mainland", "fee_naira": 3000})
        assert patch_res.status_code == 200
        assert patch_res.json()["name"] == "Mainland"
        assert patch_res.json()["fee_kobo"] == 300000

        delete_res = client.delete(f"/api/v1/delivery-zones/{zone_id}")
        assert delete_res.status_code == 200
        assert delete_res.json() == {"ok": True}

        list_after_delete = client.get("/api/v1/delivery-zones")
        assert list_after_delete.status_code == 200
        assert list_after_delete.json() == []

    app.dependency_overrides.clear()


def test_delivery_zone_tenant_scoping() -> None:
    engine = _test_engine()
    _seed_business(engine, business_id=1, name="Biz One", store_code="BIZ1")
    _seed_business(engine, business_id=2, name="Biz Two", store_code="BIZ2")

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        app.dependency_overrides[get_current_business_id] = lambda: 1
        create_res = client.post("/api/v1/delivery-zones", json={"name": "Island", "fee_naira": 2500})
        zone_id = create_res.json()["id"]

        app.dependency_overrides[get_current_business_id] = lambda: 2
        patch_res = client.patch(f"/api/v1/delivery-zones/{zone_id}", json={"name": "No Access"})
        assert patch_res.status_code == 404

        list_res = client.get("/api/v1/delivery-zones")
        assert list_res.status_code == 200
        assert list_res.json() == []

    app.dependency_overrides.clear()
