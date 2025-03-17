from app.core.db import get_database_session  # Import database connection
from app.services.tide_service import TideService

from app.repositories.tide_repository import TideRepository

async def get_tide_service():
    db_session = get_database_session()  # ✅ Pass database connection to repository
    tide_repository = TideRepository(db_session)
    return TideService(tide_repository)
