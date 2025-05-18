from algorithms.alns.operators.operator_strategy import OperatorStrategy
from algorithms.solution_state import SolutionState
from algorithms.heuristics.random_domination import repair
import numpy.random as random


class RandomRepair(OperatorStrategy):

    def __init__(
        self,
        rng: random.Generator = random.default_rng(),
    ):
        super().__init__("random")
        self._rng = rng

    def _modify_solution(self, current_solution) -> SolutionState:
        return repair(current_solution, self._rng)

    def _update_state_info(self, curr_S):
        pass
