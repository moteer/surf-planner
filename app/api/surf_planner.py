from fastapi import APIRouter

router = APIRouter()

@router.get("/surf-planner")
def get_surf_plan():
    return {"message": "Surf plan data here"}
