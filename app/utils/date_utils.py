"""Date utility functions for surf planning."""
from datetime import date, timedelta
from typing import List, Tuple
from enum import Enum


class TimePeriod(str, Enum):
    """Enum for time period types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


def get_next_sunday(d: date) -> date:
    """
    Calculate the next Sunday from any given date.
    
    Args:
        d: The starting date
        
    Returns:
        The next Sunday (or the same date if it's already Sunday)
    """
    days_ahead = (6 - d.weekday()) % 7  # Sunday is 6
    return d + timedelta(days=days_ahead)


def get_saturday_after_sunday(sunday: date) -> date:
    """
    Get the Saturday following a given Sunday.
    
    Args:
        sunday: A Sunday date
        
    Returns:
        The Saturday that comes 6 days after the given Sunday
    """
    return sunday + timedelta(days=6)


def is_sunday(d: date) -> bool:
    """
    Check if a given date is a Sunday.
    
    Args:
        d: The date to check
        
    Returns:
        True if the date is a Sunday, False otherwise
    """
    return d.weekday() == 6


def get_week_dates(sunday: date) -> List[date]:
    """
    Get all dates in a week starting from Sunday.
    
    Args:
        sunday: The Sunday that starts the week
        
    Returns:
        A list of dates from Sunday to Saturday
    """
    return [sunday + timedelta(days=i) for i in range(7)]


def get_week_start_end(reference_date: date) -> Tuple[date, date]:
    """
    Get the start (Sunday) and end (Saturday) of the week containing the reference date.
    
    Args:
        reference_date: Any date within the week
        
    Returns:
        Tuple of (start_date, end_date) where start_date is Sunday and end_date is Saturday
    """
    # Calculate days to subtract to get to Sunday (0 = Monday, 6 = Sunday)
    days_since_sunday = (reference_date.weekday() + 1) % 7
    start_date = reference_date - timedelta(days=days_since_sunday)
    end_date = start_date + timedelta(days=6)
    return start_date, end_date


def get_month_start_end(reference_date: date) -> Tuple[date, date]:
    """
    Get the start and end of the month containing the reference date.
    
    Args:
        reference_date: Any date within the month
        
    Returns:
        Tuple of (start_date, end_date) for the month
    """
    start_date = date(reference_date.year, reference_date.month, 1)
    
    # Get first day of next month, then subtract one day
    if reference_date.month == 12:
        next_month = date(reference_date.year + 1, 1, 1)
    else:
        next_month = date(reference_date.year, reference_date.month + 1, 1)
    
    end_date = next_month - timedelta(days=1)
    return start_date, end_date


def split_date_range_by_period(
    start_date: date, 
    end_date: date, 
    period: TimePeriod
) -> List[Tuple[date, date]]:
    """
    Split a date range into periods (daily, weekly, or monthly).
    
    Args:
        start_date: The start of the date range
        end_date: The end of the date range
        period: The period type (daily, weekly, monthly)
        
    Returns:
        List of tuples, each containing (period_start, period_end)
    """
    periods = []
    current = start_date
    
    if period == TimePeriod.DAILY:
        while current <= end_date:
            periods.append((current, current))
            current += timedelta(days=1)
    
    elif period == TimePeriod.WEEKLY:
        # Start from the Sunday of the week containing start_date
        week_start, week_end = get_week_start_end(current)
        
        while week_start <= end_date:
            # Clamp to the requested date range
            period_start = max(week_start, start_date)
            period_end = min(week_end, end_date)
            periods.append((period_start, period_end))
            
            # Move to next week
            week_start += timedelta(days=7)
            week_end += timedelta(days=7)
    
    elif period == TimePeriod.MONTHLY:
        while current <= end_date:
            month_start, month_end = get_month_start_end(current)
            
            # Clamp to the requested date range
            period_start = max(month_start, start_date)
            period_end = min(month_end, end_date)
            periods.append((period_start, period_end))
            
            # Move to next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
    
    return periods
