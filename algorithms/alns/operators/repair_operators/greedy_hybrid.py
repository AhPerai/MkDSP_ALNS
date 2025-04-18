from algorithms.alns.operators.operator_strategy import OperatorStrategy
from algorithms.solution_state import SolutionState, Index
from algorithms.heuristics.greedy_hybrid_v1 import repair, calc_weight


import numpy.random as random
from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy
from tests.utils.state_info_assertions import (
    assert_state_equal,
    init_state_k_degree_weight,
)


class GreedyHybridOperator(OperatorStrategy):

    def __init__(self):
        super().__init__("hybrid_greedy")
        self._info_indexes += [Index.DEGREE, Index.WEIGHT]

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        return repair(curr_S)

    def _update_state_info(self, curr_S: SolutionState) -> SolutionState:
        if curr_S.is_solution_empty():
            curr_S.reset_G_info()
            return curr_S

        for v in curr_S.non_dominated:
            for u in curr_S.G[v]:
                curr_S.G_info[u][Index.DEGREE] += 1

        for u in curr_S.non_dominated:
            curr_S.G_info[u][Index.WEIGHT] = calc_weight(
                int(curr_S.G_info[u][Index.K]),
                int(curr_S.G_info[u][Index.DEGREE]),
                len(curr_S.non_dominated),
            )

        return curr_S


def debug_state_difference(
    S_updated, S_expected, i, SEED, check_only_non_dominated=False
):
    print(
        f"\n[DEBUG] Iteration {i} | SEED {SEED} | Checking solution state differences"
    )

    if S_updated.S != S_expected.S:
        diff = S_updated.S ^ S_expected.S
        print(f"[DIFF] Solution sets differ:\n  Symmetric difference: {diff}")
    else:
        print("[OK] Solution sets match.")

    if S_updated.dominated != S_expected.dominated:
        only_in_updated = S_updated.dominated - S_expected.dominated
        only_in_expected = S_expected.dominated - S_updated.dominated
        print("[DIFF] Dominated sets differ:")
        print(f"  In updated but not expected: {only_in_updated}")
        print(f"  In expected but not updated: {only_in_expected}")
    else:
        print("[OK] Dominated sets match.")

    if S_updated.non_dominated != S_expected.non_dominated:
        diff = S_updated.non_dominated ^ S_expected.non_dominated
        print(f"[DIFF] Non-dominated sets differ:\n  Symmetric difference: {diff}")
    else:
        print("[OK] Non-dominated sets match.")

    nodes_to_check = (
        S_updated.non_dominated if check_only_non_dominated else S_updated.G.nodes()
    )

    count = 0
    for v in nodes_to_check:
        if S_updated.G_info[v] != S_expected.G_info[v]:
            print(f"[DIFF] Node {v} info differs:")
            print(f"  S_updated.G_info[{v}]: {S_updated.G_info[v]}")
            print(f"  S_expected.G_info[{v}]: {S_expected.G_info[v]}")
            count += 1
        else:
            pass  # Optional:

    print(f"{count}/{len(S_expected.non_dominated)} didnt match")


if __name__ == "__main__":
    # Configuration parameters
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/york.txt"
    DESTROY_FACTOR = 0.05
    SEED = 1234
    ITERATIONS = 100
    # Create the initial solution state
    S = SolutionState(INSTANCE_PATH, K)
    rng = random.default_rng(SEED)
    d_factor = int(len(S.G) * DESTROY_FACTOR)

    # Initialing operators
    random_repair_op = RandomRepair(rng)
    degree_repair_op = GreedyHybridOperator()
    destroy_op = RandomDestroy(d_factor, rng)
    degree_repair_op.init_state_info(S)
    S = degree_repair_op.operate(S)

    # Run the cycle for N iterations
    for i in range(ITERATIONS):
        # Step 1: Destroy part of the solution
        S_destroyed = destroy_op.operate(S)  # Step 1: Destroy some nodes

        if rng.random() < 0.7:
            # Step 2a: Update state manually
            S_updated = degree_repair_op._update_state_info(S_destroyed)
            S_expected = init_state_k_degree_weight(S_destroyed, calc_weight)

            # Compare both ways of building the state
            debug_state_difference(S_updated, S_expected, i, SEED, True)

            # Step 2b: Reconstruct with the repair operator
            S_modified = degree_repair_op._modify_solution(S_updated)
            S_expected = init_state_k_degree_weight(S_modified, calc_weight)

            # Validate again
            debug_state_difference(S_modified, S_expected, i, SEED, True)
        else:
            # Use a different operator
            S_updated = random_repair_op.operate(S_destroyed)

        S = S_updated
