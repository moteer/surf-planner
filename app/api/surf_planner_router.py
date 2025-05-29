from app.data.sql_alchemey_repository_impl import SQLAlchemySurfPlanRepositoryImpl
from app.services.surf_plan_service import SurfPlanService
from app.core.db import get_db
from sqlalchemy.orm import Session
from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, Response
from fastapi import APIRouter

router = APIRouter()

# @router.get("/surfplan")
# def get_surf_plan(date: Optional[date] = Query(None),
#             session: Session = Depends(get_db)):
#     surf_plan_service = SurfPlanService(SQLAlchemySurfPlanRepositoryImpl(session))
#
#     return surf_plan_service.generate_surf_plan_for_day_and_location(date)

