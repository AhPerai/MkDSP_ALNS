from algorithms.alns.operators.operator_strategy import IOperatorStrategy
from algorithms.solution_state import SolutionState, Index
from algorithms.heuristics.greedy_degree import repair
import pprint


class GreedyDegreeOperator(IOperatorStrategy):

    def __init__(self):
        super().__init__("degree_greedy")

    def operate(self, curr_S: SolutionState) -> SolutionState:
        return repair(curr_S, self._K)

    def _init_state_info(self, curr_S: SolutionState) -> None:
        curr_S.G_info = [[curr_S.K, curr_S.G.degree[node]] for node in curr_S.G.nodes()]

    def _update_state_info(self, curr_S):
        pass


if __name__ == "__main__":
    K = 2
    S = SolutionState("instances/test_instances/g10-50-1234.graph", K)
    print(S.G_info)

    operator = GreedyDegreeOperator()
    operator.init_state_info(S)
    pprint.pprint(S.G_info)
