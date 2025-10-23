"""Date utility functions for surf planning."""
from datetime import date, timedelta
from typing import List


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
