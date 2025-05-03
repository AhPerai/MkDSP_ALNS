import pytest
import numpy.random as random
from algorithms.solution_state import SolutionState, Index
from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy


def are_solution_states_equal(sol1: SolutionState, sol2: SolutionState) -> bool:
    return (
        sol1.K == sol2.K
        and sol1.S == sol2.S
        and sol1.dominated == sol2.dominated
        and sol1.non_dominated == sol2.non_dominated
        and len(sol1.G_info) == len(sol2.G_info)
        and all(sol1.G_info[Index.K] == sol2.G_info[Index.K] for _ in sol1.G_info)
    )


def are_solution_states_different(sol1: SolutionState, sol2: SolutionState) -> bool:
    return not are_solution_states_equal(sol1, sol2)


def are_copied_objects_address_different(
    sol1: SolutionState, sol2: SolutionState
) -> bool:
    return (
        sol1.S is not sol2.S
        and sol1.dominated is not sol2.dominated
        and sol1.non_dominated is not sol2.non_dominated
        and sol1.G_info is not sol2.G_info
        and all(sol1.G_info[Index.K] is not sol2.G_info[Index.K] for _ in sol1.G_info)
    )


def test_solution_copy():
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/york.txt"
    SEED = 1234
    rng = random.default_rng(SEED)

    S = SolutionState(INSTANCE_PATH, K)

    random_repair_op = RandomRepair(rng)
    random_repair_op.init_state_info(S)
    initial_S = random_repair_op.operate(S)
    copied_S = initial_S.copy()

    # Assert deep equality between curr_S and its copy
    assert are_solution_states_equal(
        initial_S, copied_S
    ), "copied_S should be equal in values to initial_S"
    assert are_copied_objects_address_different(
        initial_S, copied_S
    ), "copied_S should be alocated in different memory space to initial_S"


def test_solution_copy_after_change():
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/york.txt"
    DESTROY_FACTOR = 0.5
    SEED = 1234

    S = SolutionState(INSTANCE_PATH, K)
    rng = random.default_rng(SEED)

    random_repair_op = RandomRepair(rng)
    random_destroy_op = RandomDestroy(DESTROY_FACTOR, rng)

    random_repair_op.init_state_info(S)
    initial_S = random_repair_op.operate(S)
    destroyed_S = random_destroy_op.operate(initial_S.copy())

    # After destruction, the solution should differ, both in memory location and in values
    assert are_solution_states_different(
        initial_S, destroyed_S
    ), "Destroyed solution should differ from original"
    assert are_copied_objects_address_different(
        initial_S, destroyed_S
    ), "copied_S should be alocated in different memory space to destroyed_S"

    new_S = random_repair_op.operate(destroyed_S)

    """
    After reparing the solution, the values must match, as it was changed from the previous solution
    The memory location must also be the same
    """
    assert are_solution_states_equal(
        destroyed_S, new_S
    ), "New repaired solution should be equal from destroyed"
    assert not are_copied_objects_address_different(
        destroyed_S, new_S
    ), "New repaired must hold the same memory id as destroyed solution"

    # The new solution after repair should differ from the original copy
    assert are_solution_states_different(
        initial_S, new_S
    ), "New repaired solution should differ from original"
    assert are_copied_objects_address_different(
        initial_S, new_S
    ), "Initial_S should be different from new_S"

    print("All assertions passed successfully.")
