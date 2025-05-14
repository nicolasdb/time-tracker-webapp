from fastapi import APIRouter
from .diagnostics import router as diagnostics_router

router = APIRouter(
    prefix="/api",
    tags=["api"],
)

# Include all API routers
router.include_router(diagnostics_router, prefix="")  # Already has /api prefix
