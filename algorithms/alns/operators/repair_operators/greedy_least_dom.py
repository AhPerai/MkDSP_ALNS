from algorithms.alns.operators.operator_strategy import OperatorStrategy
from algorithms.solution_state import SolutionState
from algorithms.heuristics.greedy_least_dom_v1 import (
    pseudo_greedy_repair,
    greedy_repair,
)


class GreedyLeastDominatedOperator(OperatorStrategy):

    def __init__(self, greedy_alpha: float):
        super().__init__("least_dominated")
        if not (0 <= greedy_alpha <= 1):
            raise ValueError("Must be a float equal or between 0 and 1")
        self._alpha = greedy_alpha

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        # return greedy_repair(curr_S)
        return pseudo_greedy_repair(curr_S, self._alpha)

    def _update_state_info(self, curr_S: SolutionState) -> SolutionState:
        if curr_S.is_solution_empty():
            curr_S.reset_G_info()

        return curr_S
