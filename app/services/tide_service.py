import datetime

from app.repositories.tide_repository import TideRepository

class TideService:
    """Service to deal with Tides"""
    def __init__(self, tide_repository: TideRepository):
        """Constructor for TideService class
        :param tide_repository: Tide repository
        """
        self.tide_repository = tide_repository

    def get_tides_for_day_and_location(self, date: datetime, location_id: int):
        """Return all Tides for a given date and location.
        :param date: datetime.
        :param location_id: location.
        """
        tides = self.tide_repository.get_tide_by_date_and_location(date, location_id)
        return tides