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
        print("-- REPAIRING THE SOLUTION --")
        return repair(curr_S)

    def _init_state_info(self, curr_S: SolutionState) -> None:
        curr_S.G_info = [[curr_S.K, curr_S.G.degree[node]] for node in curr_S.G.nodes()]

    def _update_state_info(self, curr_S):
        for v in curr_S.non_dominated:
            for u in curr_S.G[v]:
                if u in curr_S.non_dominated:
                    curr_S.G_info[u][Index.DEGREE] += 1


if __name__ == "__main__":
    # Configuration parameters
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/york.txt"
    DESTROY_FACTOR = 0.05
    SEED = 1234
    ITERATIONS = 100

    # Create the initial solution state
    S = SolutionState(INSTANCE_PATH, K)

    # Initialize the repair operator (GreedyDegreeOperator) and the destroy operator
    repair_op = GreedyDegreeOperator()
    S = repair_op.operate(S)  # First repair (builds the initial solution)

    rng = random.default_rng(SEED)
    d_factor = int(len(S.G) * DESTROY_FACTOR)
    destroy_op = RandomDestroy(d_factor, rng)

    # Run the cycle for ITERATIONS iterations
    for i in range(ITERATIONS):
        # Step 1: Destroy some nodes
        S_destroyed = destroy_op.operate(S)

        # Step 2: Repair the destroyed solution — this triggers _update_state_info internally
        S_updated = repair_op.operate(S_destroyed)

        # Step 3: Recompute a fresh state as a reference
        S_expected = init_state_by_solution(S_updated)

        # Step 4: Check and print comparisons between S_updated and S_expected
        print(f"\n--- Iteration {i+1} ---")
        print(f"Solution sets match:        {S_updated.S == S_expected.S}")
        print(
            f"Dominated sets match:       {S_updated.dominated == S_expected.dominated}"
        )
        print(
            f"Non-dominated sets match:   {S_updated.non_dominated == S_expected.non_dominated}"
        )

        # Verify that G_info (e.g., K and Degree values) match for all nodes
        deg_match = all(
            S_updated.G_info[v] == S_expected.G_info[v] for v in S_updated.G.nodes()
        )
        print(f"Node info (K, Degree, etc.) match: {deg_match}")

        # Optionally print differences for debugging purposes:
        # for v in S_updated.G.nodes():
        #     if S_updated.G_info[v] != S_expected.G_info[v]:
        #         print(f"Node {v}: Updated {S_updated.G_info[v]}, Expected {S_expected.G_info[v]}")

        # Update S for the next iteration
        S = S_updated
