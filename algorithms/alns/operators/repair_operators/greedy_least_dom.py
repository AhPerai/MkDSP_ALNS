from algorithms.alns.operators.operator_strategy import OperatorStrategy
from algorithms.solution_state import SolutionState
from algorithms.heuristics.greedy_least_dom_v1 import repair


class GreedyLeastDominatedOperator(OperatorStrategy):

    def __init__(self):
        super().__init__("least_dom_greedy")

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        return repair(curr_S)

    def _update_state_info(self, curr_S: SolutionState) -> SolutionState:
        if curr_S.is_solution_empty():
            curr_S.reset_G_info()

        return curr_S
