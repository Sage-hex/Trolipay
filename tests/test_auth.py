import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlmodel")
pytest.importorskip("jose")

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session
from app.main import app


def test_register_login_me_flow_and_error_shape() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        register_payload = {
            "business_name": "Blessing Cakes",
            "store_code": "BLESSING",
            "email": "owner@example.com",
            "password": "secret123",
        }
        register_response = client.post("/api/v1/auth/register", json=register_payload)
        assert register_response.status_code == 200
        assert "access_token" in register_response.json()

        conflict_response = client.post("/api/v1/auth/register", json=register_payload)
        assert conflict_response.status_code == 409
        assert conflict_response.json() == {
            "error": {
                "code": "CONFLICT",
                "message": "Store code or email already exists",
                "details": None,
            }
        }

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "owner@example.com", "password": "secret123"},
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]

        me_response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {access_token}"})
        assert me_response.status_code == 200
        me_json = me_response.json()
        assert me_json["user"]["email"] == "owner@example.com"
        assert me_json["business"]["store_code"] == "BLESSING"

    app.dependency_overrides.clear()
