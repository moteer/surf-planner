"""Analytics API endpoints for surf planner statistics."""
import logging
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.data.sql_alchemey_repository_impl import SQLAlchemyStudentRepositoryImpl
from app.services.analytics_service import AnalyticsService
from app.utils.date_utils import TimePeriod

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/age-groups")
def get_age_group_statistics(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    session: Session = Depends(get_db)
):
    """
    Get count of guests by age group (Adults, Teens, Kids).
    
    Parameters:
    - start_date: Start date for the analysis period
    - end_date: End date for the analysis period
    
    Returns:
    - Dictionary with age group counts
    """
    logger.info(f"GET /analytics/age-groups called with start_date={start_date}, end_date={end_date}")
    
    # Default to today if no dates provided
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = date.today()
    
    # Validate dates
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    analytics_service = AnalyticsService(SQLAlchemyStudentRepositoryImpl(session))
    return analytics_service.get_age_group_statistics(start_date, end_date)


@router.get("/surf-lessons")
def get_surf_lesson_statistics(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    session: Session = Depends(get_db)
):
    """
    Get comprehensive surf lesson statistics.
    
    Parameters:
    - start_date: Start date for the analysis period
    - end_date: End date for the analysis period
    
    Returns:
    - Dictionary with lesson statistics including total guests, guests with/without lessons,
      average lessons, and lesson distribution
    """
    logger.info(f"GET /analytics/surf-lessons called with start_date={start_date}, end_date={end_date}")
    
    # Default to today if no dates provided
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = date.today()
    
    # Validate dates
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    analytics_service = AnalyticsService(SQLAlchemyStudentRepositoryImpl(session))
    return analytics_service.get_surf_lesson_statistics(start_date, end_date)


@router.get("/skill-levels")
def get_skill_level_distribution(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    session: Session = Depends(get_db)
):
    """
    Get distribution of surf skill levels (only counts guests who have booked lessons).
    
    Parameters:
    - start_date: Start date for the analysis period
    - end_date: End date for the analysis period
    
    Returns:
    - Dictionary with skill level counts
    """
    logger.info(f"GET /analytics/skill-levels called with start_date={start_date}, end_date={end_date}")
    
    # Default to today if no dates provided
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = date.today()
    
    # Validate dates
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    analytics_service = AnalyticsService(SQLAlchemyStudentRepositoryImpl(session))
    return analytics_service.get_level_distribution(start_date, end_date)


@router.get("/monthly/{year}")
def get_monthly_overview(
    year: int,
    session: Session = Depends(get_db)
):
    """
    Get monthly overview for an entire year.
    
    Parameters:
    - year: The year to analyze (e.g., 2024)
    
    Returns:
    - List of dictionaries with monthly statistics including guests, lessons,
      and age group breakdown per month
    """
    logger.info(f"GET /analytics/monthly/{year} called")
    
    # Validate year
    if year < 2020 or year > 2100:
        raise HTTPException(status_code=400, detail="Year must be between 2020 and 2100")
    
    analytics_service = AnalyticsService(SQLAlchemyStudentRepositoryImpl(session))
    return analytics_service.get_monthly_overview(year)


@router.get("/comprehensive")
def get_comprehensive_statistics(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    session: Session = Depends(get_db)
):
    """
    Get all statistics combined.
    
    Parameters:
    - start_date: Start date for the analysis period
    - end_date: End date for the analysis period
    
    Returns:
    - Dictionary containing all statistics (age groups, surf lessons, skill levels)
    """
    logger.info(f"GET /analytics/comprehensive called with start_date={start_date}, end_date={end_date}")
    
    # Default to today if no dates provided
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = date.today()
    
    # Validate dates
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    analytics_service = AnalyticsService(SQLAlchemyStudentRepositoryImpl(session))
    return analytics_service.get_comprehensive_statistics(start_date, end_date)


@router.get("/flexible")
def get_flexible_analytics(
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    period: TimePeriod = Query(TimePeriod.WEEKLY, description="Time period granularity (daily, weekly, monthly)"),
    filters: Optional[List[str]] = Query(
        None,
        description="Metrics to include. Options: teens, adults, kids, total_guests, "
                   "surf_lessons, yoga_lessons, skate_lessons, beginner, beginner_plus, "
                   "intermediate, advanced, teen_students, kid_students"
    ),
    session: Session = Depends(get_db)
):
    """
    Get flexible analytics data with customizable time periods and filters.
    
    This endpoint allows you to:
    - Choose between daily, weekly, or monthly time periods
    - Filter which metrics to include in the response
    - Analyze any date range
    
    Parameters:
    - start_date: Start date for the analysis period (required)
    - end_date: End date for the analysis period (required)
    - period: Time granularity - daily, weekly (default), or monthly
    - filters: List of metrics to include (if not specified, returns all metrics)
    
    Returns:
    - List of dictionaries, each containing analytics for one time period
    
    Example filters:
    - For age groups: teens, adults, kids
    - For lesson counts: surf_lessons, yoga_lessons, skate_lessons
    - For skill levels: beginner, beginner_plus, intermediate, advanced, teen_students, kid_students
    - For totals: total_guests
    """
    logger.info(f"GET /analytics/flexible called with start_date={start_date}, end_date={end_date}, period={period}, filters={filters}")
    
    # Validate dates
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    # Convert filters list to set for efficient lookup
    filter_set = set(filters) if filters else None
    
    # Validate filters if provided
    valid_filters = {
        'teens', 'adults', 'kids', 'total_guests',
        'surf_lessons', 'yoga_lessons', 'skate_lessons',
        'beginner', 'beginner_plus', 'intermediate', 'advanced',
        'teen_students', 'kid_students'
    }
    
    if filter_set:
        invalid_filters = filter_set - valid_filters
        if invalid_filters:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid filters: {invalid_filters}. Valid filters are: {valid_filters}"
            )
    
    analytics_service = AnalyticsService(SQLAlchemyStudentRepositoryImpl(session))
    return analytics_service.get_flexible_analytics(start_date, end_date, period, filter_set)
