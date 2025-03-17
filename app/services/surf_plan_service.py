import datetime

from app.repositories.tide_repository import TideRepository


def generateFancyurfPlanLogicThaMakesEverythinAwesome(guests):
    pass


class SurfPlanService:
    def __init__(self, tide_repository: TideRepository):
        self.tide_repository = tide_repository

    def generate_surf_plan_for_day_and_location(self, date: datetime, location_id: int):
        # check if surfplan exits already and dicide to keep or throw error

        #guests = guest_repoitory.get_guests_by_day(date)

        surf_plan = generateFancyurfPlanLogicThaMakesEverythinAwesome(guests)

        #surf_plan_repostory.save(surf_plan)
