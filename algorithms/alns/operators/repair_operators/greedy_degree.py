from algorithms.alns.operators.operator_strategy import IOperatorStrategy
from algorithms.solution_state import SolutionState, Index
from algorithms.heuristics.greedy_degree import repair

# For testing purposes
import pprint
import numpy.random as random
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy
from algorithms.heuristics.greedy_degree import init_state_by_solution


class GreedyDegreeOperator(IOperatorStrategy):

    def __init__(self):
        super().__init__("degree_greedy")

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        return repair(curr_S)

    def _init_state_info(self, curr_S: SolutionState) -> SolutionState:
        curr_S.G_info = [[curr_S.K, curr_S.G.degree[node]] for node in curr_S.G.nodes()]
        return curr_S

    def _update_state_info(self, curr_S) -> SolutionState:
        for v in curr_S.non_dominated:
            for u in curr_S.G[v]:
                if u in curr_S.non_dominated:
                    curr_S.G_info[u][Index.DEGREE] += 1
        return curr_S


if __name__ == "__main__":
    # Step 1: Initialize and repair once
    K = 2
    S = SolutionState("instances/test_instances/g10-50-1234.graph", K)

    repair_op = GreedyDegreeOperator()
    S = repair_op.operate(S)

    # Step 2: Destroy some nodes
    SEED = 1234
    DESTROY_FACTOR = 0.05
    rng = random.default_rng(SEED)
    destroy_op = RandomDestroy(int(len(S.G) * DESTROY_FACTOR), rng)

    S_destroyed = destroy_op.operate(S)

    # Step 3: Repair again — this will trigger _update_state_info
    S_updated = repair_op.operate(S_destroyed)

    # Step 4: Create a fresh, clean state to compare with
    S_expected = init_state_by_solution(S_updated)

    # Step 5: Check if both states match
    print("\n--- State Consistency Check ---")
    print(f"Solution sets match:        {S_updated.S == S_expected.S}")
    print(f"Dominated sets match:       {S_updated.dominated == S_expected.dominated}")
    print(
        f"Non-dominated sets match:   {S_updated.non_dominated == S_expected.non_dominated}"
    )

    # for v in S_updated.G.nodes():
    #     if S_updated.G_info[v] != S_expected.G_info[v]:
    #         print(
    #             f"❌ Node {v}: Expected {S_expected.G_info[v]}, Got {S_updated.G_info[v]}"
    #         )
    # check degrees and K values too
    deg_match = all(
        S_updated.G_info[v] == S_expected.G_info[v] for v in S_updated.G.nodes()
    )
    print(f"Node info (K, Degree) match: {deg_match}")
