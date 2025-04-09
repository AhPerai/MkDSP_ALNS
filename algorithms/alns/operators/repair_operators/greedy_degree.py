from algorithms.alns.operators.operator_strategy import IOperatorStrategy
from algorithms.solution_state import SolutionState
from algorithms.heuristics.greedy_degree import repair
import pprint


class GreedyDegreeOperator(IOperatorStrategy):

    def __init__(self):
        super().__init__("degree_greedy")

    def operate(self, current_solution: SolutionState) -> SolutionState:
        return repair(current_solution, self._K)

    def init_state_info(self, current_solution: SolutionState) -> None:
        if current_solution.is_state_clear():
            current_solution.G_info = [
                [current_solution.K, current_solution.G.degree[node]]
                for node in current_solution.G.nodes()
            ]


if __name__ == "__main__":
    K = 2
    S = SolutionState("instances/test_instances/g10-50-1234.graph", K)
    print(S.G_info)

    operator = GreedyDegreeOperator()
    operator.init_state_info(S)
    pprint.pprint(S.G_info)
