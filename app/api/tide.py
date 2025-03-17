from fastapi import APIRouter
from app.services.tide_service import fetch_tides_for_date_and_location

router = APIRouter()

@router.get("/tides/{date}/{location_id}")
def get_tides(date: str, location_id: int):
    return fetch_tides_for_date_and_location(date, location_id)
