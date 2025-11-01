"""Tests for date utility functions."""
import unittest
from datetime import date

from app.utils.date_utils import (
    TimePeriod,
    get_week_start_end,
    get_month_start_end,
    split_date_range_by_period
)


class TestDateUtils(unittest.TestCase):
    """Tests for date utility functions."""

    def test_get_week_start_end_from_monday(self):
        """Test getting week boundaries from a Monday."""
        # Monday, June 2, 2025
        monday = date(2025, 6, 2)
        start, end = get_week_start_end(monday)
        
        # Should return Sunday June 1 to Saturday June 7
        self.assertEqual(start, date(2025, 6, 1))
        self.assertEqual(end, date(2025, 6, 7))

    def test_get_week_start_end_from_sunday(self):
        """Test getting week boundaries from a Sunday."""
        # Sunday, June 1, 2025
        sunday = date(2025, 6, 1)
        start, end = get_week_start_end(sunday)
        
        # Should return same Sunday to following Saturday
        self.assertEqual(start, date(2025, 6, 1))
        self.assertEqual(end, date(2025, 6, 7))

    def test_get_week_start_end_from_saturday(self):
        """Test getting week boundaries from a Saturday."""
        # Saturday, June 7, 2025
        saturday = date(2025, 6, 7)
        start, end = get_week_start_end(saturday)
        
        # Should return previous Sunday to this Saturday
        self.assertEqual(start, date(2025, 6, 1))
        self.assertEqual(end, date(2025, 6, 7))

    def test_get_month_start_end(self):
        """Test getting month boundaries."""
        # June 15, 2025
        mid_month = date(2025, 6, 15)
        start, end = get_month_start_end(mid_month)
        
        # Should return June 1 to June 30
        self.assertEqual(start, date(2025, 6, 1))
        self.assertEqual(end, date(2025, 6, 30))

    def test_get_month_start_end_december(self):
        """Test getting month boundaries for December."""
        # December 15, 2025
        mid_december = date(2025, 12, 15)
        start, end = get_month_start_end(mid_december)
        
        # Should return December 1 to December 31
        self.assertEqual(start, date(2025, 12, 1))
        self.assertEqual(end, date(2025, 12, 31))

    def test_split_date_range_by_daily(self):
        """Test splitting a date range into daily periods."""
        start = date(2025, 6, 1)
        end = date(2025, 6, 3)
        
        periods = split_date_range_by_period(start, end, TimePeriod.DAILY)
        
        # Should return 3 days
        self.assertEqual(len(periods), 3)
        self.assertEqual(periods[0], (date(2025, 6, 1), date(2025, 6, 1)))
        self.assertEqual(periods[1], (date(2025, 6, 2), date(2025, 6, 2)))
        self.assertEqual(periods[2], (date(2025, 6, 3), date(2025, 6, 3)))

    def test_split_date_range_by_weekly(self):
        """Test splitting a date range into weekly periods."""
        # June 1-14, 2025 (Sunday to Sunday)
        start = date(2025, 6, 1)
        end = date(2025, 6, 14)
        
        periods = split_date_range_by_period(start, end, TimePeriod.WEEKLY)
        
        # Should return 2 full weeks
        self.assertEqual(len(periods), 2)
        self.assertEqual(periods[0], (date(2025, 6, 1), date(2025, 6, 7)))
        self.assertEqual(periods[1], (date(2025, 6, 8), date(2025, 6, 14)))

    def test_split_date_range_by_weekly_partial(self):
        """Test splitting a date range into weekly periods with partial weeks."""
        # June 3-10, 2025 (Tuesday to Tuesday)
        start = date(2025, 6, 3)
        end = date(2025, 6, 10)
        
        periods = split_date_range_by_period(start, end, TimePeriod.WEEKLY)
        
        # Should return 2 periods, first partial week and second partial week
        self.assertEqual(len(periods), 2)
        # First period: Tuesday June 3 to Saturday June 7 (clamped to start date)
        self.assertEqual(periods[0], (date(2025, 6, 3), date(2025, 6, 7)))
        # Second period: Sunday June 8 to Tuesday June 10 (clamped to end date)
        self.assertEqual(periods[1], (date(2025, 6, 8), date(2025, 6, 10)))

    def test_split_date_range_by_monthly(self):
        """Test splitting a date range into monthly periods."""
        # June 1 to August 31, 2025
        start = date(2025, 6, 1)
        end = date(2025, 8, 31)
        
        periods = split_date_range_by_period(start, end, TimePeriod.MONTHLY)
        
        # Should return 3 months
        self.assertEqual(len(periods), 3)
        self.assertEqual(periods[0], (date(2025, 6, 1), date(2025, 6, 30)))
        self.assertEqual(periods[1], (date(2025, 7, 1), date(2025, 7, 31)))
        self.assertEqual(periods[2], (date(2025, 8, 1), date(2025, 8, 31)))

    def test_split_date_range_by_monthly_partial(self):
        """Test splitting a date range into monthly periods with partial months."""
        # June 15 to July 10, 2025
        start = date(2025, 6, 15)
        end = date(2025, 7, 10)
        
        periods = split_date_range_by_period(start, end, TimePeriod.MONTHLY)
        
        # Should return 2 periods, both partial months
        self.assertEqual(len(periods), 2)
        self.assertEqual(periods[0], (date(2025, 6, 15), date(2025, 6, 30)))
        self.assertEqual(periods[1], (date(2025, 7, 1), date(2025, 7, 10)))


if __name__ == '__main__':
    unittest.main()
