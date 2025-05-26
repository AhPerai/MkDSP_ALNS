from algorithms.alns.operators.operator_strategy import (
    OperatorStrategy,
    OperatorContext,
)
from algorithms.solution_state import SolutionState
from algorithms.heuristics.greedy_least_dom_v1 import pseudo_greedy_repair
import numpy.random as random


class GreedyLeastDominatedOperator(OperatorStrategy):
    name = "least_dominated_repair"

    def __init__(
        self,
        greedy_alpha: float,
        rng: random.Generator = random.default_rng(),
    ):
        super().__init__()
        if not (0 <= greedy_alpha <= 1):
            raise ValueError("Must be a float equal or between 0 and 1")
        self._alpha = greedy_alpha
        self._rng = rng

    @classmethod
    def get_instance_from_context(cls, context: OperatorContext):
        return cls(context.greedy_alpha, context.rng)

    def reset(self, rng=None):
        self._rng = rng

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        return pseudo_greedy_repair(curr_S, self._alpha, self._rng)

    def _update_state_info(self, curr_S: SolutionState) -> SolutionState:
        if curr_S.is_solution_empty():
            curr_S.reset_G_info()

        return curr_S
