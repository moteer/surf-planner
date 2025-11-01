"""Tests for analytics service."""
import unittest
from unittest.mock import Mock
from datetime import date

from app.services.analytics_service import AnalyticsService
from app.domain.repositories_interfaces import StudentRepositoryInterface
from app.utils.date_utils import TimePeriod
from test.test_helpers import create_test_student


class TestAnalyticsService(unittest.TestCase):
    """Tests for AnalyticsService."""

    def setUp(self):
        """Set up test data."""
        self.mock_repository = Mock(spec=StudentRepositoryInterface)
        self.analytics_service = AnalyticsService(self.mock_repository)
        
        # Create test students with various attributes
        self.test_students = [
            # Adults with lessons
            create_test_student(id=1, age_group="Adults >18 years", level="BEGINNER", number_of_surf_lessons=3),
            create_test_student(id=2, age_group="Adults >18 years", level="INTERMEDIATE", number_of_surf_lessons=5),
            create_test_student(id=3, age_group="Adults >18 years", level="BEGINNER PLUS", number_of_surf_lessons=4),
            # Teens with lessons
            create_test_student(id=4, age_group="Teens 13-18", level="BEGINNER", number_of_surf_lessons=2),
            create_test_student(id=5, age_group="Teens 13-18", level="BEGINNER", number_of_surf_lessons=3),
            # Kids with lessons
            create_test_student(id=6, age_group="Kids 5-12", level="BEGINNER", number_of_surf_lessons=2),
            # Adults without lessons
            create_test_student(id=7, age_group="Adults >18 years", level="BEGINNER", number_of_surf_lessons=0),
            # Cancelled bookings (should be excluded)
            create_test_student(id=8, age_group="Adults >18 years", booking_status="cancelled", number_of_surf_lessons=3),
        ]
        
        self.mock_repository.get_all.return_value = self.test_students

    def test_get_age_group_statistics(self):
        """Test getting age group statistics."""
        stats = self.analytics_service.get_age_group_statistics(
            date(2025, 6, 1), 
            date(2025, 6, 7)
        )
        
        # Should count active students only (excluding cancelled)
        self.assertEqual(stats['adults'], 4)  # IDs 1, 2, 3, 7
        self.assertEqual(stats['teens'], 2)   # IDs 4, 5
        self.assertEqual(stats['kids'], 1)    # ID 6
        self.assertEqual(stats['total'], 7)
        
        self.mock_repository.get_all.assert_called_once()

    def test_get_surf_lesson_statistics(self):
        """Test getting surf lesson statistics."""
        stats = self.analytics_service.get_surf_lesson_statistics(
            date(2025, 6, 1), 
            date(2025, 6, 7)
        )
        
        self.assertEqual(stats['total_guests'], 7)
        self.assertEqual(stats['guests_with_lessons'], 6)  # IDs 1-6
        self.assertEqual(stats['guests_without_lessons'], 1)  # ID 7
        
        # Average lessons: (3+5+4+2+3+2) / 6 = 19/6 ≈ 3.17
        self.assertAlmostEqual(stats['average_lessons'], 3.17, places=2)
        
        # Check lesson distribution
        self.assertEqual(stats['lesson_distribution'][2], 2)  # 2 students with 2 lessons
        self.assertEqual(stats['lesson_distribution'][3], 2)  # 2 students with 3 lessons
        self.assertEqual(stats['lesson_distribution'][4], 1)  # 1 student with 4 lessons
        self.assertEqual(stats['lesson_distribution'][5], 1)  # 1 student with 5 lessons
        
        self.mock_repository.get_all.assert_called_once()

    def test_get_level_distribution(self):
        """Test getting skill level distribution."""
        stats = self.analytics_service.get_level_distribution(
            date(2025, 6, 1), 
            date(2025, 6, 7)
        )
        
        # Only students with lessons should be counted
        self.assertEqual(stats['beginner'], 1)       # ID 1
        self.assertEqual(stats['beginner_plus'], 1)  # ID 3
        self.assertEqual(stats['intermediate'], 1)   # ID 2
        self.assertEqual(stats['advanced'], 0)
        self.assertEqual(stats['teens'], 2)          # IDs 4, 5
        self.assertEqual(stats['kids'], 1)           # ID 6
        
        self.mock_repository.get_all.assert_called_once()

    def test_get_comprehensive_statistics(self):
        """Test getting comprehensive statistics."""
        stats = self.analytics_service.get_comprehensive_statistics(
            date(2025, 6, 1), 
            date(2025, 6, 7)
        )
        
        # Check that all statistics are included
        self.assertIn('age_groups', stats)
        self.assertIn('surf_lessons', stats)
        self.assertIn('skill_levels', stats)
        self.assertIn('period', stats)
        
        # Verify age groups
        self.assertEqual(stats['age_groups']['adults'], 4)
        self.assertEqual(stats['age_groups']['teens'], 2)
        self.assertEqual(stats['age_groups']['kids'], 1)
        
        # Verify surf lessons
        self.assertEqual(stats['surf_lessons']['total_guests'], 7)
        self.assertEqual(stats['surf_lessons']['guests_with_lessons'], 6)
        
        # Verify skill levels
        self.assertEqual(stats['skill_levels']['beginner'], 1)
        
        # Verify period
        self.assertEqual(stats['period']['start_date'], '2025-06-01')
        self.assertEqual(stats['period']['end_date'], '2025-06-07')


class TestFlexibleAnalytics(unittest.TestCase):
    """Tests for flexible analytics functionality."""

    def setUp(self):
        """Set up test data."""
        self.mock_repository = Mock(spec=StudentRepositoryInterface)
        self.analytics_service = AnalyticsService(self.mock_repository)
        
        # Create test students with yoga and skate lessons
        self.test_students = [
            # Week 1: June 1-7
            create_test_student(
                id=1, age_group="Adults >18 years", level="BEGINNER",
                arrival=date(2025, 6, 1), departure=date(2025, 6, 7),
                number_of_surf_lessons=3, number_of_yoga_lessons=2, number_of_skate_lessons=1
            ),
            create_test_student(
                id=2, age_group="Teens 13-18",
                arrival=date(2025, 6, 1), departure=date(2025, 6, 7),
                number_of_surf_lessons=2, number_of_yoga_lessons=1, number_of_skate_lessons=0
            ),
            # Week 2: June 8-14
            create_test_student(
                id=3, age_group="Kids 5-12",
                arrival=date(2025, 6, 8), departure=date(2025, 6, 14),
                number_of_surf_lessons=2, number_of_yoga_lessons=0, number_of_skate_lessons=2
            ),
            create_test_student(
                id=4, age_group="Adults >18 years", level="INTERMEDIATE",
                arrival=date(2025, 6, 8), departure=date(2025, 6, 14),
                number_of_surf_lessons=5, number_of_yoga_lessons=3, number_of_skate_lessons=0
            ),
        ]
        
        self.mock_repository.get_all.return_value = self.test_students

    def test_flexible_analytics_weekly_all_filters(self):
        """Test flexible analytics with weekly periods and all filters."""
        results = self.analytics_service.get_flexible_analytics(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 14),
            period=TimePeriod.WEEKLY,
            filters=None  # Include all metrics
        )
        
        # Should return 2 weeks
        self.assertEqual(len(results), 2)
        
        # Check first week (June 1-7)
        week1 = results[0]
        self.assertEqual(week1['period_start'], '2025-06-01')
        self.assertEqual(week1['period_end'], '2025-06-07')
        self.assertEqual(week1['total_guests'], 2)
        self.assertEqual(week1['adults'], 1)
        self.assertEqual(week1['teens'], 1)
        self.assertEqual(week1['kids'], 0)
        self.assertEqual(week1['surf_lessons'], 5)  # 3 + 2
        self.assertEqual(week1['yoga_lessons'], 3)  # 2 + 1
        self.assertEqual(week1['skate_lessons'], 1)  # 1 + 0
        
        # Check second week (June 8-14)
        week2 = results[1]
        self.assertEqual(week2['period_start'], '2025-06-08')
        self.assertEqual(week2['period_end'], '2025-06-14')
        self.assertEqual(week2['total_guests'], 2)
        self.assertEqual(week2['adults'], 1)
        self.assertEqual(week2['teens'], 0)
        self.assertEqual(week2['kids'], 1)
        self.assertEqual(week2['surf_lessons'], 7)  # 2 + 5
        self.assertEqual(week2['yoga_lessons'], 3)  # 0 + 3
        self.assertEqual(week2['skate_lessons'], 2)  # 2 + 0

    def test_flexible_analytics_weekly_with_filters(self):
        """Test flexible analytics with specific filters."""
        results = self.analytics_service.get_flexible_analytics(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 14),
            period=TimePeriod.WEEKLY,
            filters={'total_guests', 'surf_lessons', 'yoga_lessons'}
        )
        
        # Should return 2 weeks
        self.assertEqual(len(results), 2)
        
        # Check first week - should only have requested fields plus period info
        week1 = results[0]
        self.assertIn('period_start', week1)
        self.assertIn('period_end', week1)
        self.assertIn('total_guests', week1)
        self.assertIn('surf_lessons', week1)
        self.assertIn('yoga_lessons', week1)
        # Should NOT have skate_lessons or age group breakdowns
        self.assertNotIn('skate_lessons', week1)
        self.assertNotIn('adults', week1)
        self.assertNotIn('teens', week1)

    def test_flexible_analytics_daily(self):
        """Test flexible analytics with daily periods."""
        results = self.analytics_service.get_flexible_analytics(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            period=TimePeriod.DAILY,
            filters={'total_guests', 'surf_lessons'}
        )
        
        # Should return 3 days
        self.assertEqual(len(results), 3)
        
        # Each day should have the same guests (since they stay June 1-7)
        for i, day_result in enumerate(results):
            self.assertEqual(day_result['total_guests'], 2)
            self.assertEqual(day_result['surf_lessons'], 5)

    def test_flexible_analytics_monthly(self):
        """Test flexible analytics with monthly periods."""
        results = self.analytics_service.get_flexible_analytics(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 30),
            period=TimePeriod.MONTHLY,
            filters={'total_guests', 'adults', 'teens', 'kids'}
        )
        
        # Should return 1 month
        self.assertEqual(len(results), 1)
        
        month = results[0]
        self.assertEqual(month['period_start'], '2025-06-01')
        self.assertEqual(month['period_end'], '2025-06-30')
        # All 4 students overlap with June
        self.assertEqual(month['total_guests'], 4)
        self.assertEqual(month['adults'], 2)
        self.assertEqual(month['teens'], 1)
        self.assertEqual(month['kids'], 1)

    def test_flexible_analytics_skill_level_filters(self):
        """Test flexible analytics with skill level filters."""
        results = self.analytics_service.get_flexible_analytics(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 14),
            period=TimePeriod.WEEKLY,
            filters={'beginner', 'intermediate', 'teen_students', 'kid_students'}
        )
        
        # Check first week
        week1 = results[0]
        self.assertEqual(week1['beginner'], 1)  # ID 1
        self.assertEqual(week1.get('intermediate', 0), 0)  # No intermediate in week 1
        self.assertEqual(week1['teen_students'], 1)  # ID 2
        self.assertEqual(week1['kid_students'], 0)
        
        # Check second week
        week2 = results[1]
        self.assertEqual(week2.get('beginner', 0), 0)  # No beginner in week 2
        self.assertEqual(week2['intermediate'], 1)  # ID 4
        self.assertEqual(week2['teen_students'], 0)
        self.assertEqual(week2['kid_students'], 1)  # ID 3


if __name__ == '__main__':
    unittest.main()
