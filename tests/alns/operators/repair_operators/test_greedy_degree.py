import pytest

import numpy.random as random
from algorithms.solution_state import SolutionState, Index
from algorithms.alns.operators.repair_operators.greedy_degree import (
    GreedyDegreeOperator,
)
from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy
from tests.utils.state_info_assertions import assert_state_equal, init_state_k_degree
from tests.utils.valid_solution_assertions import (
    validate_operator_solution_dominates_graph,
    validate_operator_generate_valid_solution,
)


# Test instances
instances = [
    ("instances/cities_small_instances/belfast.txt", 2),
    ("instances/cities_small_instances/newcastle.txt", 2),
    ("instances/cities_small_instances/coventry.txt", 2),
]


greedy_alphas = [0, 0.3, 1]


@pytest.mark.parametrize("operator_class", [GreedyDegreeOperator])
@pytest.mark.parametrize("greedy_alpha", greedy_alphas)
@pytest.mark.parametrize("instance_path,K", instances)
def test_greedy_degree_operator_generate_valid_solution(
    operator_class, instance_path, K, greedy_alpha
):
    validate_operator_generate_valid_solution(
        operator_class, instance_path, K, greedy_alpha
    )


@pytest.mark.parametrize("operator_class", [GreedyDegreeOperator])
@pytest.mark.parametrize("greedy_alpha", greedy_alphas)
@pytest.mark.parametrize("instance_path,K", instances)
def test_greedy_degree_operator_dominates_graph(
    operator_class, instance_path, K, greedy_alpha
):
    validate_operator_solution_dominates_graph(
        operator_class, instance_path, K, greedy_alpha
    )


@pytest.mark.parametrize("iterations", [100])
def test_update_state_consistency(iterations):
    # Configuration parameters
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/york.txt"
    DESTROY_FACTOR = 0.5
    SEED = 1234
    GREEDY_ALPHA = 0.3
    # Create the initial solution state
    S = SolutionState(INSTANCE_PATH, K)
    rng = random.default_rng(SEED)

    # Initialing operators
    random_repair_op = RandomRepair(rng)
    main_operator = GreedyDegreeOperator(GREEDY_ALPHA)
    destroy_op = RandomDestroy(DESTROY_FACTOR, rng)

    main_operator.init_state_info(S)
    S = main_operator.operate(S)

    # Run the cycle for N iterations
    for i in range(iterations):
        # Step 1: Destroy part of the solution
        S_destroyed = destroy_op.operate(S)  # Step 1: Destroy some nodes

        if rng.random() < 0.7:
            # Step 2a: Update state manually
            S_updated = main_operator._update_state_info(S_destroyed)
            S_expected = init_state_k_degree(S_destroyed)

            # Compare both ways of building the state
            assert_state_equal(S_updated, S_expected, i, SEED, [Index.K, Index.DEGREE])

            # Step 2b: Reconstruct with the repair operator
            S_modified = main_operator._modify_solution(S_updated)
            S_expected = init_state_k_degree(S_modified)

            # Validate again
            assert_state_equal(S_modified, S_expected, i, SEED, [Index.K, Index.DEGREE])
        else:
            # Use a different operator
            S_updated = random_repair_op.operate(S_destroyed)

        S = S_updated
