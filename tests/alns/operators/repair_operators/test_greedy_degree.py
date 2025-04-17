import pytest

import numpy.random as random
from algorithms.solution_state import SolutionState
from algorithms.alns.operators.repair_operators.greedy_degree import (
    GreedyDegreeOperator,
)
from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy
from tests.utils.test_utils import assert_state_equal, init_state_k_degree


# def test_greedy_operator_generates_valid_solution():
#     S = SolutionState("instances/cities_small_instances/york.txt", 2)
#     op = GreedyDegreeOperator()
#     op.init_state_info(S)
#     S = op.operate(S)

#     assert len(S.non_dominated) == 0
#     assert all(u in S.S or any(v in S.S for v in S.G[u]) for u in S.G)


@pytest.mark.parametrize("iterations", [100])
def test_update_state_consistency(iterations):
    # Configuration parameters
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/york.txt"
    DESTROY_FACTOR = 0.05
    SEED = 1234
    # Create the initial solution state
    S = SolutionState(INSTANCE_PATH, K)
    rng = random.default_rng(SEED)
    d_factor = int(len(S.G) * DESTROY_FACTOR)

    # Initialing operators
    random_repair_op = RandomRepair(rng)
    degree_repair_op = GreedyDegreeOperator()
    destroy_op = RandomDestroy(d_factor, rng)
    degree_repair_op.init_state_info(S)
    S = degree_repair_op.operate(S)

    # Run the cycle for N iterations
    for i in range(iterations):
        S_destroyed = destroy_op.operate(S)  # Step 1: Destroy some nodes

        # Step 2: Just making sure the main operator isnt called every time
        if rng.random() < 0.7:

            S_updated = degree_repair_op._update_state_info(S_destroyed)
            S_expected = init_state_k_degree(S_destroyed)
            assert_state_equal(S_updated, S_expected, i, SEED)

            S_updated = degree_repair_op.operate(S_destroyed)
            S_expected = init_state_k_degree(S_updated)
            assert_state_equal(S_updated, S_expected, i, SEED)
        else:
            S_updated = random_repair_op.operate(S_destroyed)

        S = S_updated
