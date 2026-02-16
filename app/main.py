from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1 import router as api_v1_router
from app.core.config import get_settings

settings = get_settings()


media_root = Path(settings.media_dir)
(media_root / "products").mkdir(parents=True, exist_ok=True)
(media_root / "receipts").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ChatCommerce v1")
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
app.include_router(api_v1_router)


@app.get("/api/v1/health")
def health() -> dict[str, bool]:
    return {"ok": True}
