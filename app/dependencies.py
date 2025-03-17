from app.db import database  # Import database connection
from app.services.tide_service import TideService

from app.repositories.tide_repository import TideRepository


async def get_user_service():
    db_session = database  # ✅ Pass database connection to repository
    tide_repository = TideRepository(db_session)
    return TideService(tide_repository)
