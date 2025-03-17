import datetime

from app.repositories.tide_repository import TideRepository

class TideService:
    def __init__(self, tide_repository: TideRepository):
        self.tide_repository = tide_repository

    def get_tides_for_day_and_location(self, date: datetime, location_id: int):
        tides = self.tide_repository.get_tide_by_date_and_location(date, location_id)
        return tides