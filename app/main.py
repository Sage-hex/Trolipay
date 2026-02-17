from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import router as api_v1_router
from app.core.errors import AppError
from app.core.config import get_settings

settings = get_settings()


media_root = Path(settings.media_dir)
(media_root / "products").mkdir(parents=True, exist_ok=True)
(media_root / "receipts").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ChatCommerce v1")
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
app.include_router(api_v1_router)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    status_code = 400
    if exc.code == "AUTH_ERROR":
        status_code = 401
    elif exc.code == "NOT_FOUND":
        status_code = 404
    elif exc.code == "CONFLICT":
        status_code = 409

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": None,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": None,
            }
        },
    )


@app.get("/api/v1/health")
def health() -> dict[str, bool]:
    return {"ok": True}
