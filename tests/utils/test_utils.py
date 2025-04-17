from typing import Callable
from algorithms.solution_state import SolutionState, Index
import copy


def assert_state_equal(S_updated, S_expected, i, SEED, check_only_non_dominated=False):
    assert S_updated.S == S_expected.S, (
        f"[FAIL] Iteration {i} | SEED {SEED} | Solution sets differ.\n"
        f"Symmetric difference: {S_updated.S ^ S_expected.S}"
    )
    assert S_updated.dominated == S_expected.dominated, (
        f"[FAIL] Iteration {i} | SEED {SEED} | Dominated sets differ.\n"
        f"Symmetric difference: {len(S_updated.dominated)} - {len(S_expected.dominated)}"
    )
    assert S_updated.non_dominated == S_expected.non_dominated, (
        f"[FAIL] Iteration {i} | SEED {SEED} | Non-dominated sets differ.\n"
        f"Symmetric difference: {S_updated.non_dominated ^ S_expected.non_dominated}"
    )

    nodes_to_check = (
        S_updated.non_dominated if check_only_non_dominated else S_updated.G.nodes()
    )

    for v in nodes_to_check:
        assert S_updated.G_info[v] == S_expected.G_info[v], (
            f"[FAIL] Iteration {i} | SEED {SEED} | Node {v} info differs.\n"
            f"S_updated.G_info[{v}]: {S_updated.G_info[v]}\n"
            f"S_expected.G_info[{v}]: {S_expected.G_info[v]}"
        )


def init_state_k_only(current_S: SolutionState) -> SolutionState:
    expected_state = copy.deepcopy(current_S)

    if expected_state.is_solution_empty():
        return expected_state

    expected_state.dominated = set()
    expected_state.non_dominated = set(expected_state.G.nodes())

    expected_state.add_info_index([Index.K])
    expected_state.init_G_info()

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
    expected_state = init_state_k_degree(current_S)

    if expected_state.is_solution_empty():
        return expected_state

    expected_state.dominated = set()
    expected_state.non_dominated = set(expected_state.G.nodes())

    expected_state.add_info_index([Index.K, Index.DEGREE, Index.WEIGHT])
    expected_state.init_G_info()

    G = expected_state.G

    for v in expected_state.S:

        for u in current_S.non_dominated:
            current_S.G_info[u][Index.WEIGHT] = calc_weight(
                int(current_S.G_info[u][Index.K]),
                int(current_S.G_info[u][Index.DEGREE]),
                len(current_S.non_dominated),
            )

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
