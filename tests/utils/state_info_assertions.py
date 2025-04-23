from typing import Callable
from algorithms.solution_state import SolutionState, Index
import copy


def assert_state_equal(
    given_solution,
    expected_solution,
    i,
    SEED,
    info_to_check=None,
    nodes_to_check=None,
):

    nodes_to_check = (
        expected_solution.G.nodes() if nodes_to_check == None else nodes_to_check
    )

    if info_to_check is None:
        info_to_check = [Index.K]

    assert (
        given_solution.S == expected_solution.S
    ), f"[FAIL] Solution sets differ at iteration {i}, seed {SEED}"
    assert (
        given_solution.dominated == expected_solution.dominated
    ), f"[FAIL] Dominated sets differ at iteration {i}, seed {SEED}"
    assert (
        given_solution.non_dominated == expected_solution.non_dominated
    ), f"[FAIL] Non-dominated sets differ at iteration {i}, seed {SEED}"

    for v in nodes_to_check:
        for index in info_to_check:
            assert (
                given_solution.G_info[v][index] == expected_solution.G_info[v][index]
            ), (
                f"[FAIL] Iteration {i} | SEED {SEED} | Node {v} info differs.\n"
                f"given{v}    : {given_solution.G_info[v]}\n"
                f"expected {v}: {expected_solution.G_info[v]}"
            )


def init_state_k_only(current_S: SolutionState) -> SolutionState:
    expected_state = copy.deepcopy(current_S)

    if expected_state.is_solution_empty():
        return expected_state

    expected_state.dominated = set()
    expected_state.non_dominated = set(expected_state.G.nodes())

    expected_state.reset_G_info()

    G = expected_state.G

    for v in expected_state.S:
        for u in G[v]:
            expected_state.G_info[u][Index.K] -= 1

            if expected_state.G_info[u][Index.K] == 0 and u not in expected_state.S:
                expected_state.dominated.add(u)
                expected_state.non_dominated.discard(u)

        expected_state.non_dominated.discard(v)

    return expected_state


def init_state_k_degree(current_S: SolutionState) -> SolutionState:
    expected_state = copy.deepcopy(current_S)

    if expected_state.is_solution_empty():
        return expected_state

    expected_state.dominated = set()
    expected_state.non_dominated = set(expected_state.G.nodes())

    expected_state.reset_G_info()

    G = expected_state.G

    for v in expected_state.S:
        for u in G[v]:
            expected_state.G_info[u][Index.K] -= 1

            if expected_state.G_info[u][Index.DEGREE] > 0:
                expected_state.G_info[u][Index.DEGREE] -= 1

            if expected_state.G_info[u][Index.K] == 0 and u not in expected_state.S:
                expected_state.dominated.add(u)
                expected_state.non_dominated.discard(u)
                for w in G[u]:
                    if expected_state.G_info[w][Index.DEGREE] > 0:
                        expected_state.G_info[w][Index.DEGREE] -= 1

        expected_state.non_dominated.discard(v)

    return expected_state


def init_state_k_degree_weight(
    current_S: SolutionState, calc_weight: Callable[[int, int, int], float]
) -> SolutionState:
    expected_state = copy.deepcopy(current_S)

    if expected_state.is_solution_empty():
        return expected_state

    expected_state.dominated = set()
    expected_state.non_dominated = set(expected_state.G.nodes())

    expected_state.reset_G_info()

    G = expected_state.G

    for v in expected_state.S:

        for u in G[v]:
            expected_state.G_info[u][Index.K] -= 1

            if expected_state.G_info[u][Index.DEGREE] > 0:
                expected_state.G_info[u][Index.DEGREE] -= 1

            if expected_state.G_info[u][Index.K] == 0 and u not in expected_state.S:
                expected_state.dominated.add(u)
                expected_state.non_dominated.discard(u)
                for w in G[u]:
                    if expected_state.G_info[w][Index.DEGREE] > 0:
                        expected_state.G_info[w][Index.DEGREE] -= 1

        expected_state.non_dominated.discard(v)

        for v in expected_state.non_dominated:
            expected_state.G_info[v][Index.WEIGHT] = calc_weight(
                int(expected_state.G_info[v][Index.K]),
                int(expected_state.G_info[v][Index.DEGREE]),
                len(expected_state.non_dominated),
            )

    return expected_state
