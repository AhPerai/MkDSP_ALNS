from algorithms.alns.operators.operator_strategy import IOperatorStrategy
from algorithms.solution_state import SolutionState
from algorithms.heuristics.random_domination import repair
import numpy.random as random


class RandomRepair(IOperatorStrategy):

    def __init__(
        self,
        rng: random.Generator = random.default_rng(),
    ):
        super().__init__("random_repair")
        self._rng = rng

    def _modify_solution(self, current_solution) -> SolutionState:
        return repair(current_solution, self._rng)

    def _init_state_info(self, curr_S):
        curr_S.G_info = [[curr_S.K] for _ in curr_S.G.nodes()]

    def _update_state_info(self, curr_S):
        pass
