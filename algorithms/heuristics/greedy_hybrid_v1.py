from algorithms.solution_state import SolutionState, Index


def __calc_weight(dom_value: int, degree: int, n_nodes: int) -> float:
    factor: float = (dom_value * dom_value) / (n_nodes - degree)
    return factor


def repair(current_S: SolutionState) -> SolutionState:
    G = current_S.G

    while len(current_S.non_dominated) > 0:
        v = next(iter(current_S.non_dominated))

        if len(current_S.non_dominated) > 0:
            for u in current_S.non_dominated:
                current_S.G_info[u][Index.WEIGHT] = __calc_weight(
                    int(current_S.G_info[u][Index.K]),
                    int(current_S.G_info[u][Index.DEGREE]),
                    len(current_S.non_dominated),
                )
                if (
                    current_S.G_info[u][Index.WEIGHT]
                    > current_S.G_info[v][Index.WEIGHT]
                ):
                    v = u

        current_S.S.add(v)

        for u in G[v]:
            # dominate the neighbors of V
            current_S.G_info[u][Index.K] -= 1

            # update the node degree as the edge between U and V is no longer relevant
            if current_S.G_info[u][Index.DEGREE] > 0:
                current_S.G_info[u][Index.DEGREE] -= 1

            # discard u, update the node degree between u and its neightboors, as u is no longer relevant
            if current_S.G_info[u][Index.K] == 0 and u not in current_S.S:
                current_S.dominated.add(u)
                current_S.non_dominated.discard(u)
                for w in G[u]:
                    # update the node degree as the edge between U and W is no longer relevant
                    if current_S.G_info[w][Index.DEGREE] > 0:
                        current_S.G_info[w][Index.DEGREE] -= 1

        current_S.non_dominated.discard(v)

    return current_S


if __name__ == "__main__":
    K = 2
    S = SolutionState("instances/cities_small_instances/belfast.txt", K)
    print(f"Solution initialized: {S.is_state_clear()}")
    S.G_info = [
        [
            S.K,
            S.G.degree[node],
            __calc_weight(S.K, S.G.degree[node], len(S.non_dominated)),
        ]
        for node in S.G.nodes()
    ]
    S = repair(S)
    print(len(S.S))
