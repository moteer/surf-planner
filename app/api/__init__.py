from fastapi import APIRouter
from app.api import tide, surf_planner

router = APIRouter()

# Include all individual routers
router.include_router(tide.router, prefix="/tides", tags=["Tides"])
router.include_router(surf_planner.router, prefix="/surf-planner", tags=["Surf Planner"])
