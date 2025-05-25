from algorithms.alns.operators.operator_strategy import (
    OperatorStrategy,
    OperatorContext,
)
from algorithms.solution_state import SolutionState, Index
from algorithms.heuristics.greedy_hybrid_v2 import pseudo_greedy_repair


class GreedyHybridDegreeOperator(OperatorStrategy):
    name = "hybrid_remaining_neighbor_repair"

    def __init__(self, greedy_alpha: float):
        super().__init__()
        if not (0 <= greedy_alpha <= 1):
            raise ValueError("Must be a float equal or between 0 and 1")
        self._alpha = greedy_alpha
        self._info_indexes += [Index.DEGREE, Index.WEIGHT]

    @classmethod
    def get_instance_from_context(cls, context: OperatorContext):
        return cls(context.greedy_alpha)

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        return pseudo_greedy_repair(curr_S, self._alpha)

    def _update_state_info(self, curr_S: SolutionState) -> SolutionState:
        if curr_S.is_solution_empty():
            curr_S.reset_G_info()
            return curr_S

        for v in curr_S.non_dominated:
            for u in curr_S.G[v]:
                curr_S.G_info[u][Index.DEGREE] += 1

        return curr_S
