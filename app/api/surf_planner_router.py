from app.services.student_service import StudentService
from fastapi import APIRouter

router = APIRouter()

@router.get("/students")
def get_surf_plan():

    return surfplan
