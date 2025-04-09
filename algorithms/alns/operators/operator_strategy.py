from abc import ABC, abstractmethod
from algorithms.solution_state import SolutionState


class IOperatorStrategy(ABC):

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def operate(self, current_solution: SolutionState) -> SolutionState:
        return NotImplemented

    def _prepare_solution(self, current_solution: SolutionState) -> SolutionState:
        pass
