"""Tests for analytics service."""
import unittest
from unittest.mock import Mock
from datetime import date

from app.services.analytics_service import AnalyticsService
from app.domain.repositories_interfaces import StudentRepositoryInterface
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


if __name__ == '__main__':
    unittest.main()
