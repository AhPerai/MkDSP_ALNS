import pytest

from algorithms.solution_state import SolutionState, Index
from algorithms.alns.operators.repair_operators.greedy_hybrid import (
    GreedyHybridOperator,
)

from tests.utils.valid_solution_assertions import (
    validate_operator_solution_dominates_graph,
    validate_operator_generate_valid_solution,
)

import numpy.random as random
from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy
from tests.utils.state_info_assertions import (
    assert_state_equal,
    init_state_k_degree_weight,
)

from algorithms.heuristics.greedy_hybrid_v1 import calc_weight


@pytest.mark.parametrize("operator_class", [GreedyHybridOperator])
@pytest.mark.parametrize(
    "instance_path,K", [("instances/cities_small_instances/york.txt", 2)]
)
def test_greedy_hybrid_operator_generate_valid_solution(
    operator_class, instance_path, K
):
    validate_operator_generate_valid_solution(operator_class, instance_path, K)


@pytest.mark.parametrize("operator_class", [GreedyHybridOperator])
@pytest.mark.parametrize(
    "instance_path,K", [("instances/cities_small_instances/york.txt", 2)]
)
def test_greedy_hybrid_operator_dominates_graph(operator_class, instance_path, K):
    validate_operator_solution_dominates_graph(operator_class, instance_path, K)


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
    degree_repair_op = GreedyHybridOperator()
    destroy_op = RandomDestroy(d_factor, rng)
    degree_repair_op.init_state_info(S)
    S = random_repair_op.operate(S)

    # Run the cycle for N iterations
    for i in range(iterations):
        # Step 1: Destroy part of the solution
        S_destroyed = destroy_op.operate(S)  # Step 1: Destroy some nodes

        if rng.random() < 0.5:
            # Step 2a: Update state manually
            S_updated = degree_repair_op._update_state_info(S_destroyed)
            S_expected = init_state_k_degree_weight(S_destroyed, calc_weight)

            # Compare both ways of building the state
            assert_state_equal(S_updated, S_expected, i, SEED, [Index.K, Index.DEGREE])

            # Step 2b: Reconstruct with the repair operator
            S_modified = degree_repair_op._modify_solution(S_updated)
            S_expected = init_state_k_degree_weight(S_modified, calc_weight)

            # Validate again
            assert_state_equal(S_modified, S_expected, i, SEED, [Index.K, Index.DEGREE])
        else:
            # Use a different operator
            S_updated = random_repair_op.operate(S_destroyed)

        S = S_updated
