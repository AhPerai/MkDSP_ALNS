from algorithms.alns.operators.operator_strategy import IOperatorStrategy
from algorithms.solution_state import SolutionState
from algorithms.solution_state import Index
import numpy.random as random

# from algorithms.alns.operators.repair_operators.greedy_degree import (
#     GreedyDegreeOperator,
# )
# from algorithms.heuristics.greedy_degree import init_state_by_solution
# from algorithms.utils.graph_visualizer import Visualizer
# import pprint


class RandomDestroy(IOperatorStrategy):

    def __init__(
        self,
        remove_value: int,
        rng: random.Generator = random.default_rng(),
    ):
        super().__init__("random")
        self._remove_value = remove_value
        self._rng = rng

    @property
    def remove_value(self) -> str:
        return self._remove_value

    def _modify_solution(self, current_solution):
        to_remove = self._rng.choice(
            list(current_solution.S), size=self.remove_value, replace=False
        )

        # remove nodes that are part of the current solution
        for v in to_remove:
            # when V is removed its checked if V has been dominated by other nodes, if K > 0 it's not dominated
            current_solution.S.remove(v)

            if current_solution.G_info[v][Index.K] > 0:
                current_solution.non_dominated.add(v)
            else:
                current_solution.dominated.add(v)

            # un-dominate V's neighboors
            for u in current_solution.G[v]:

                if current_solution.G_info[u][Index.K] < current_solution.K:
                    current_solution.G_info[u][Index.K] += 1

                # if U's K-value is greater than 0 and is not part of the solution is
                if (
                    current_solution.G_info[u][Index.K] > 0
                    and u not in current_solution.S
                ):
                    current_solution.dominated.discard(u)
                    current_solution.non_dominated.add(u)

        return current_solution

    def _init_state_info(self, current_solution):
        pass

    def _update_state_info(self, current_solution):
        pass


if __name__ == "__main__":
    K = 2
    S = SolutionState("instances/cities_small_instances/liverpool.txt", K)

    r_operator = GreedyDegreeOperator()
    r_operator._init_state_info(S)
    S = r_operator.operate(S)
    print(f"Initial Solution size: {len(S.S)}")
    print(f"Intersection - Solution and Dominated: {len(S.S & S.dominated)}")
    print(f"Intersection - Solution and Non-dominated: {len(S.S & S.non_dominated)}")
    print(
        f"Intersection - Non-dominated and Dominated: {len(S.non_dominated & S.dominated)}"
    )

    SEED = 7654
    DESTROY_FACTOR = 0.05
    rng = random.default_rng(SEED)
    d_factor = int(len(S.G) * DESTROY_FACTOR)
    print(f"\ngrau de destruição: {d_factor} ")

    d_operator = RandomDestroy(d_factor, rng)
    S = d_operator.operate(S)

    corrected_S = init_state_by_solution(S)

    # vis = Visualizer(S.G)
    # vis.print_as_adjlist()

    print(f"Solution sets are equivalent: {S.S == corrected_S.S}")
    print(f"Dominated node sets are equivalent: {S.dominated == corrected_S.dominated}")
    print(
        f"Non-Dominated node sets are equivalent: {S.non_dominated == corrected_S.non_dominated}"
    )
    # pprint.pprint(S.non_dominated)
