from fastapi import APIRouter
from app.api import students_router
from app.api import surf_planner_router

router = APIRouter()

# Include all individual routers
router.include_router(students_router.router, prefix="/students", tags=["Surf Planner"])
router.include_router(surf_planner_router.router, prefix="/surfplan", tags=["Surf Planner"])
