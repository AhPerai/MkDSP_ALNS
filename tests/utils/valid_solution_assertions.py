from algorithms.solution_state import SolutionState, Index


def validate_operator_solution_dominates_graph(
    operator_class, instance_path, K, greedy_alpha
):
    S = SolutionState(instance_path, K)
    op = operator_class(greedy_alpha)
    op.init_state_info(S)
    S = op.operate(S)

    assert len(S.non_dominated) == 0
    __assert_dominated_solution(S)


def validate_operator_generate_valid_solution(
    operator_class, instance_path, K, greedy_alpha
):
    S = SolutionState(instance_path, K)
    operator = operator_class(greedy_alpha)
    operator.init_state_info(S)
    S = operator.operate(S)

    # Only nodes in the solution can have K > 0
    for node in S.G.nodes():
        k_val = S.G_info[node][Index.K]
        if node not in S.S:
            assert (
                k_val <= 0
            ), f"[FAIL] Node {node} is not in the solution set but has G_info[K] = {k_val}, expected ≤ 0"

    # Dominated set + Solution set must cover all nodes
    total_nodes = len(S.G.nodes())
    covered_nodes = len(S.dominated) + len(S.S)
    assert covered_nodes == total_nodes, (
        f"[FAIL] Dominated ({len(S.dominated)}) + Solution ({len(S.S)}) = {covered_nodes}, "
        f"but expected {total_nodes} (total nodes)"
    )

    # Non-dominated set must be empty
    assert (
        not S.non_dominated
    ), f"[FAIL] Non-dominated set is not empty: {S.non_dominated}"


def __assert_dominated_solution(solution: SolutionState):
    for v in solution.G.nodes():
        if v in solution.S:
            continue
        count = sum(1 for u in solution.G[v] if u in solution.S)
        assert (
            count >= solution.K
        ), f"[FAIL] Node {v} has only {count} neighbors in solution (expected at least {solution.K})"
