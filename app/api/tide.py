from fastapi import APIRouter
from app.services.tide_service import TideService

router = APIRouter()

@router.get("/tides/{date}/{location_id}")
def get_tides(date: str, location_id: int):
    return TideService.get_tides_for_day_and_location(date, location_id)
