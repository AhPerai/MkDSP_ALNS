from abc import ABC, abstractmethod
import numpy as np


class Resettable(ABC):

    @abstractmethod
    def reset(self, rng: np.random.Generator = None) -> None:
        """Resets the component, rng is optional"""
        pass
