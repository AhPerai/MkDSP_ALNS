from abc import ABC, abstractmethod
from algorithms.solution_state import SolutionState


class IOperatorStrategy(ABC):

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def operate(self, current_solution: SolutionState) -> SolutionState:
        self._prepare_solution(current_solution)
        return self._modify_solution(current_solution)

    @abstractmethod
    def _modify_solution(self, current_solution) -> SolutionState:
        return NotImplemented

    @abstractmethod
    def _init_state_info(self, current_solution: SolutionState) -> SolutionState:
        return NotImplemented

    @abstractmethod
    def _update_state_info(self, current_solution: SolutionState) -> SolutionState:
        return NotImplemented

    def _prepare_solution(self, current_solution: SolutionState) -> SolutionState:
        if current_solution.is_state_clear():
            return self._init_state_info(current_solution)
        else:
            return self._update_state_info(current_solution)
