import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlmodel")
pytest.importorskip("jose")
pytest.importorskip("sqlalchemy")

from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session
from app.main import app


def _auth_headers(client: TestClient) -> dict[str, str]:
    payload = {
        "business_name": "Blessing Cakes",
        "store_code": "BLESSING",
        "email": "owner@example.com",
        "password": "secret123",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def test_get_business_authenticated() -> None:
    engine = _test_engine()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        headers = _auth_headers(client)
        response = client.get("/api/v1/business", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Blessing Cakes"
        assert body["store_code"] == "BLESSING"
        assert body["currency"] == "NGN"

    app.dependency_overrides.clear()


def test_patch_business_updates_name() -> None:
    engine = _test_engine()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        headers = _auth_headers(client)
        response = client.patch("/api/v1/business", json={"name": "Blessing Cakes 2"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Blessing Cakes 2"

    app.dependency_overrides.clear()


def test_patch_business_store_code_rejected() -> None:
    engine = _test_engine()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        headers = _auth_headers(client)
        response = client.patch(
            "/api/v1/business",
            json={"store_code": "NEWCODE", "name": "New Name"},
            headers=headers,
        )
        assert response.status_code == 400
        assert response.json() == {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "store_code cannot be updated",
                "details": None,
            }
        }

    app.dependency_overrides.clear()
