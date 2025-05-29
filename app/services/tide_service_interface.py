from abc import ABC, abstractmethod
from typing import Tuple
from datetime import date
import datetime

class TideServiceInterface(ABC):

    def get_low_tides(self, day: date) -> Tuple:
        pass

class TideServiceMockImpl(TideServiceInterface):
    def get_low_tides(self, day: date) -> Tuple:
        facketime = datetime.datetime(2020, 5, 17)
        return (facketime, facketime)
