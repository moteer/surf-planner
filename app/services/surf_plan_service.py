from datetime import date
from app.domain.repositories import SurfPlanRepository
from app.domain.models import SurfPlan


class SurfPlanService:
    def __init__(self, surf_plan_repository: SurfPlanRepository):
        self.surf_plan_repository = surf_plan_repository

    def generate_surf_plan_for_day_and_location(self, plan_date: date, location_id: int) -> SurfPlan:
        # Check if plan exists
        existing_plan = self.surf_plan_repository.get_by_date_and_location(plan_date, location_id)

        if existing_plan is None:
            new_plan = SurfPlan(plan_date=plan_date)
            return self.surf_plan_repository.save(new_plan)

        return existing_plan