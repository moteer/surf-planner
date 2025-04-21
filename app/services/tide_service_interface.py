from abc import ABC, abstractmethod
from typing import Tuple
from datetime import date


class TideServiceInterface(ABC):
    @abstractmethod
    def get_low_tides(self, day: date) -> Tuple:
        pass
