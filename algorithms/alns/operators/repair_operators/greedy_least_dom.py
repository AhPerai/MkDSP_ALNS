from algorithms.alns.operators.operator_strategy import (
    OperatorStrategy,
    OperatorContext,
)
from algorithms.solution_state import SolutionState
from algorithms.heuristics.greedy_least_dom_v1 import pseudo_greedy_repair


class GreedyLeastDominatedOperator(OperatorStrategy):
    name = "least_dominated_repair"

    def __init__(self, greedy_alpha: float):
        super().__init__()
        if not (0 <= greedy_alpha <= 1):
            raise ValueError("Must be a float equal or between 0 and 1")
        self._alpha = greedy_alpha

    @classmethod
    def get_instance_from_context(cls, context: OperatorContext):
        return cls(context.greedy_alpha)

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        return pseudo_greedy_repair(curr_S, self._alpha)

    def _update_state_info(self, curr_S: SolutionState) -> SolutionState:
        if curr_S.is_solution_empty():
            curr_S.reset_G_info()

        return curr_S
