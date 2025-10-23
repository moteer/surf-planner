"""Analytics service for surf planner statistics."""
import logging
from datetime import date
from typing import Dict, List
from collections import defaultdict

from app.domain.repositories_interfaces import StudentRepositoryInterface
from app.utils.student_utils import is_adult, is_teen, is_kid, is_level, filter_active_students, filter_students_with_lessons

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating analytics and statistics about surf students."""

    def __init__(self, student_repository: StudentRepositoryInterface):
        """
        Initialize the analytics service.
        
        Args:
            student_repository: Repository for accessing student data
        """
        self.student_repository = student_repository

    def get_age_group_statistics(self, start_date: date, end_date: date) -> Dict:
        """
        Get count of guests by age group (Adults, Teens, Kids).
        
        Args:
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            
        Returns:
            Dictionary with age group counts
        """
        logger.info(f"Getting age group statistics from {start_date} to {end_date}")
        
        students = self._get_students_for_period(start_date, end_date)
        active_students = filter_active_students(students)
        
        adults = sum(1 for s in active_students if is_adult(s))
        teens = sum(1 for s in active_students if is_teen(s))
        kids = sum(1 for s in active_students if is_kid(s))
        
        return {
            "adults": adults,
            "teens": teens,
            "kids": kids,
            "total": adults + teens + kids
        }

    def get_surf_lesson_statistics(self, start_date: date, end_date: date) -> Dict:
        """
        Get comprehensive surf lesson statistics.
        
        Args:
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            
        Returns:
            Dictionary with lesson statistics including:
            - total_guests: Total number of active guests
            - guests_with_lessons: Number of guests with surf lessons
            - guests_without_lessons: Number of guests without surf lessons
            - average_lessons: Average number of lessons per guest (who booked lessons)
            - lesson_distribution: Distribution of number of lessons
        """
        logger.info(f"Getting surf lesson statistics from {start_date} to {end_date}")
        
        students = self._get_students_for_period(start_date, end_date)
        active_students = filter_active_students(students)
        
        with_lessons = filter_students_with_lessons(active_students)
        without_lessons = [s for s in active_students if s.number_of_surf_lessons == 0]
        
        # Calculate average lessons
        total_lessons = sum(s.number_of_surf_lessons for s in with_lessons)
        avg_lessons = total_lessons / len(with_lessons) if with_lessons else 0
        
        # Calculate lesson distribution
        lesson_counts = defaultdict(int)
        for student in with_lessons:
            lesson_counts[student.number_of_surf_lessons] += 1
        
        return {
            "total_guests": len(active_students),
            "guests_with_lessons": len(with_lessons),
            "guests_without_lessons": len(without_lessons),
            "average_lessons": round(avg_lessons, 2),
            "lesson_distribution": dict(lesson_counts)
        }

    def get_level_distribution(self, start_date: date, end_date: date) -> Dict:
        """
        Get distribution of surf skill levels (only for students with lessons).
        
        Args:
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            
        Returns:
            Dictionary with skill level counts
        """
        logger.info(f"Getting level distribution from {start_date} to {end_date}")
        
        students = self._get_students_for_period(start_date, end_date)
        active_students = filter_active_students(students)
        with_lessons = filter_students_with_lessons(active_students)
        
        # Count by level
        beginner = sum(1 for s in with_lessons if is_adult(s) and is_level(s, "BEGINNER"))
        beginner_plus = sum(1 for s in with_lessons if is_adult(s) and is_level(s, "BEGINNER PLUS"))
        intermediate = sum(1 for s in with_lessons if is_adult(s) and is_level(s, "INTERMEDIATE"))
        advanced = sum(1 for s in with_lessons if is_adult(s) and is_level(s, "ADVANCED"))
        teens = sum(1 for s in with_lessons if is_teen(s))
        kids = sum(1 for s in with_lessons if is_kid(s))
        
        return {
            "beginner": beginner,
            "beginner_plus": beginner_plus,
            "intermediate": intermediate,
            "advanced": advanced,
            "teens": teens,
            "kids": kids
        }

    def get_monthly_overview(self, year: int) -> List[Dict]:
        """
        Get monthly overview for an entire year.
        
        Args:
            year: The year to analyze
            
        Returns:
            List of dictionaries with monthly statistics
        """
        logger.info(f"Getting monthly overview for year {year}")
        
        monthly_data = []
        
        for month in range(1, 13):
            # Get first and last day of the month
            if month == 12:
                start_date = date(year, month, 1)
                end_date = date(year, month, 31)
            else:
                start_date = date(year, month, 1)
                # Get last day of current month
                next_month = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)
                end_date = date(next_month.year, next_month.month, 1)
                # Move back one day to get last day of current month
                from datetime import timedelta
                end_date = end_date - timedelta(days=1)
            
            students = self._get_students_for_period(start_date, end_date)
            active_students = filter_active_students(students)
            with_lessons = filter_students_with_lessons(active_students)
            
            # Calculate age groups
            adults = sum(1 for s in active_students if is_adult(s))
            teens = sum(1 for s in active_students if is_teen(s))
            kids = sum(1 for s in active_students if is_kid(s))
            
            # Calculate total lessons
            total_lessons = sum(s.number_of_surf_lessons for s in with_lessons)
            
            monthly_data.append({
                "month": month,
                "month_name": date(year, month, 1).strftime("%B"),
                "total_guests": len(active_students),
                "guests_with_lessons": len(with_lessons),
                "total_lessons": total_lessons,
                "adults": adults,
                "teens": teens,
                "kids": kids
            })
        
        return monthly_data

    def get_comprehensive_statistics(self, start_date: date, end_date: date) -> Dict:
        """
        Get all statistics combined.
        
        Args:
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            
        Returns:
            Dictionary containing all statistics
        """
        logger.info(f"Getting comprehensive statistics from {start_date} to {end_date}")
        
        return {
            "age_groups": self.get_age_group_statistics(start_date, end_date),
            "surf_lessons": self.get_surf_lesson_statistics(start_date, end_date),
            "skill_levels": self.get_level_distribution(start_date, end_date),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }

    def _get_students_for_period(self, start_date: date, end_date: date) -> List:
        """
        Get students whose stay overlaps with the specified period.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            
        Returns:
            List of students
        """
        all_students = self.student_repository.get_all()
        return [
            student for student in all_students
            if student.arrival <= end_date and student.departure >= start_date
        ]
