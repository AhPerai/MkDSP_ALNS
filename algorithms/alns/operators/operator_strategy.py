from typing import List
from abc import ABC, abstractmethod
from algorithms.solution_state import SolutionState, Index
import numpy.random as random


class OperatorContext:
    def __init__(
        self,
        rng: random.Generator = random.default_rng(),
        greedy_alpha: float = 0,
        destroy_factor: float = 0.5,
    ):
        self.rng = rng
        self.greedy_alpha = greedy_alpha
        self.destroy_factor = destroy_factor


class OperatorStrategy(ABC):
    name: str = None

    def __init__(self):
        self._info_indexes: List[int] = [Index.K]

    @property
    def name(self) -> str:
        return self.__class__.name or self.__class__.__name__

    @property
    def info_indexes(self) -> List[int]:
        return self._info_indexes

    def operate(self, current_solution: SolutionState) -> SolutionState:
        if current_solution.is_state_clear():
            return current_solution

        self._update_state_info(current_solution)
        return self._modify_solution(current_solution)

    @abstractmethod
    def _modify_solution(self, current_solution) -> SolutionState:
        return NotImplemented

    @abstractmethod
    def _update_state_info(self, current_solution: SolutionState) -> SolutionState:
        return NotImplemented

    @abstractmethod
    def get_instance_from_context(cls, context):
        """Create an instance from an OperatorContext."""
        return NotImplemented

    def init_state_info(self, initial_state: SolutionState) -> None:
        initial_state.add_info_index(self.info_indexes)
        initial_state.init_G_info()
