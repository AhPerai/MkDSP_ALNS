from operators.operator_strategy import IOperatorStrategy
from algorithms.heuristics.greedy_degree import repair


class GreedyDegreeOperator(IOperatorStrategy):

    def __init__(self, K: int):
        super().__init__("degree_greedy", K)

    def operate(self, current_solution):
        return repair(current_solution, self._K)
