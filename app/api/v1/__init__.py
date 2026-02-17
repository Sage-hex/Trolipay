from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.business import router as business_router

router = APIRouter(prefix="/api/v1", tags=["v1"])
router.include_router(auth_router)
router.include_router(business_router)
