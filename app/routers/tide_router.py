from surf_conditions_data_orm import Tide

from fastapi import FastAPI, Depends
from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.services.tide_service import TideService

# FastAPI Instance
app = FastAPI(title="SurfPlanner API", description="API to get tide data", version="1.0")

# Pydantic Models for API Responses
class TideResponse(BaseModel):
    timestamp: datetime
    height: float
    type: str


class TidesResponse(BaseModel):
    date: str
    tides: List[TideResponse]


@app.get("/tides/{date}", response_model=TidesResponse)
def get_tide_by_date_and_location(date: datetime, location_id: int):
    tides = TideService.get_tides_for_day_and_location(date, location_id)

    return TidesResponse(
        date=date,
        tides=[TideResponse(timestamp=tide.timestamp, height=tide.height, type=tide.type) for tide in tides]
    )

# Run the API with Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)