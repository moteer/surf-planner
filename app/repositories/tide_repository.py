from sqlalchemy.orm import Session
from app.models.tide import Tide
from app.models.location import Location
from datetime import datetime

class TideRepository():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_tide_by_date_and_location(self, date: datetime, location_id: int):
        """
        Fetch tides by date and location using ORM filtering.
        """
        return (
            self.db_session.query(Tide)
            .filter(Tide.timestamp.between(f"{date} 00:00:00", f"{date} 23:59:59"))
            .filter(Tide.location_id == location_id)
            .all()
        )

