from fastapi import APIRouter
from app.api import students_router

router = APIRouter()

# Include all individual routers
router.include_router(students_router.router, prefix="/students", tags=["Surf Planner"])
