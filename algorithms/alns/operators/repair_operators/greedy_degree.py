from algorithms.alns.operators.operator_strategy import OperatorStrategy
from algorithms.solution_state import SolutionState, Index
from algorithms.heuristics.greedy_degree import repair


class GreedyDegreeOperator(OperatorStrategy):

    def __init__(self):
        super().__init__("degree_greedy")
        self._info_indexes.append(Index.DEGREE)

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        return repair(curr_S)

    def _init_state_info(self, curr_S: SolutionState) -> SolutionState:
        curr_S.add_info_index(self.info_indexes)
        curr_S.init_G_info()
        return curr_S

    def _update_state_info(self, curr_S: SolutionState) -> None:
        if curr_S.is_solution_empty():
            curr_S.reset_G_info()
            return

        for v in curr_S.non_dominated:
            for u in curr_S.G[v]:
                if u in curr_S.non_dominated:
                    curr_S.G_info[u][Index.DEGREE] += 1
