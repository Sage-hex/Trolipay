from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.core.config import get_settings


def create_test_engine():
    """Create an isolated test engine.

    - Default: in-memory sqlite (fast, hermetic)
    - Optional: external DB via TEST_DATABASE_URL (e.g. Neon)
    """
    settings = get_settings()
    database_url = (settings.test_database_url or "").strip()

    if database_url:
        engine = create_engine(database_url, echo=False)
    else:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    return engine
