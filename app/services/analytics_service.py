"""Analytics service for surf planner statistics."""
import logging
from datetime import date
from typing import Dict, List, Optional, Set
from collections import defaultdict

from app.domain.repositories_interfaces import StudentRepositoryInterface
from app.utils.student_utils import is_adult, is_teen, is_kid, is_level, filter_active_students, filter_students_with_lessons
from app.utils.date_utils import TimePeriod, split_date_range_by_period

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

    def get_flexible_analytics(
        self, 
        start_date: date, 
        end_date: date, 
        period: TimePeriod = TimePeriod.WEEKLY,
        filters: Optional[Set[str]] = None
    ) -> List[Dict]:
        """
        Get analytics data broken down by time periods with flexible filtering.
        
        Args:
            start_date: Start date for the analysis period
            end_date: End date for the analysis period
            period: Time period granularity (daily, weekly, monthly)
            filters: Set of metrics to include. If None, includes all metrics.
                    Valid filters: 'teens', 'adults', 'kids', 'total_guests',
                    'surf_lessons', 'yoga_lessons', 'skate_lessons',
                    'beginner', 'beginner_plus', 'intermediate', 'advanced',
                    'teen_students', 'kid_students'
            
        Returns:
            List of dictionaries with analytics data for each period
        """
        logger.info(f"Getting flexible analytics from {start_date} to {end_date} by {period}")
        
        # If no filters specified, include all metrics
        if filters is None:
            filters = {
                'teens', 'adults', 'kids', 'total_guests',
                'surf_lessons', 'yoga_lessons', 'skate_lessons',
                'beginner', 'beginner_plus', 'intermediate', 'advanced',
                'teen_students', 'kid_students'
            }
        
        # Split the date range into periods
        periods = split_date_range_by_period(start_date, end_date, period)
        
        results = []
        for period_start, period_end in periods:
            period_data = {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
            }
            
            # Get students for this period
            students = self._get_students_for_period(period_start, period_end)
            active_students = filter_active_students(students)
            
            # Calculate metrics based on filters
            if 'total_guests' in filters:
                period_data['total_guests'] = len(active_students)
            
            # Age group counts
            if 'adults' in filters:
                period_data['adults'] = sum(1 for s in active_students if is_adult(s))
            
            if 'teens' in filters:
                period_data['teens'] = sum(1 for s in active_students if is_teen(s))
            
            if 'kids' in filters:
                period_data['kids'] = sum(1 for s in active_students if is_kid(s))
            
            # Lesson counts
            if 'surf_lessons' in filters:
                period_data['surf_lessons'] = sum(s.number_of_surf_lessons for s in active_students)
            
            if 'yoga_lessons' in filters:
                period_data['yoga_lessons'] = sum(s.number_of_yoga_lessons for s in active_students)
            
            if 'skate_lessons' in filters:
                period_data['skate_lessons'] = sum(s.number_of_skate_lessons for s in active_students)
            
            # Skill level breakdown (for students with surf lessons)
            with_lessons = filter_students_with_lessons(active_students)
            
            if 'beginner' in filters:
                period_data['beginner'] = sum(1 for s in with_lessons if is_adult(s) and is_level(s, "BEGINNER"))
            
            if 'beginner_plus' in filters:
                period_data['beginner_plus'] = sum(1 for s in with_lessons if is_adult(s) and is_level(s, "BEGINNER PLUS"))
            
            if 'intermediate' in filters:
                period_data['intermediate'] = sum(1 for s in with_lessons if is_adult(s) and is_level(s, "INTERMEDIATE"))
            
            if 'advanced' in filters:
                period_data['advanced'] = sum(1 for s in with_lessons if is_adult(s) and is_level(s, "ADVANCED"))
            
            if 'teen_students' in filters:
                period_data['teen_students'] = sum(1 for s in with_lessons if is_teen(s))
            
            if 'kid_students' in filters:
                period_data['kid_students'] = sum(1 for s in with_lessons if is_kid(s))
            
            results.append(period_data)
        
        return results

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
