from algorithms.solution_state import SolutionState, Index


def repair(graph: Graph, K):
    G = graph

    """
    non_dominated = G.nodes; its a Set containing only the nodes' id
    G_info is a dict where key = node_id -> [K_value]
    S is the solution set
    """
    G_info: Dict[int, List[int]] = dict()
    non_dominated: Set[int] = set()
    S: Set[int] = set()

    for v in G.nodes():
        G_info[v] = [K]
        non_dominated.add(v)

    # main loop
    while len(non_dominated) > 0:
        v = next(iter(non_dominated))

        # select the least dominated node
        for u in non_dominated:
            if G_info[v][0] < G_info[u][0]:
                v = u

        # add the vertex to the solution
        S.add(v)

        for neighbor in G[v]:

            # dominate the neighbors of V
            if G_info[neighbor][0] > 0:
                G_info[neighbor][0] -= 1

            if G_info[neighbor][0] == 0:
                non_dominated.discard(neighbor)

        non_dominated.discard(v)

    return S


if __name__ == "__main__":
    K = 2
    S = SolutionState("instances/cities_small_instances/belfast.txt", K)
    print(f"Solution initialized: {S.is_state_clear()}")

    S.G_info = [[S.K, S.G.degree[node]] for node in S.G.nodes()]
    S = repair(S)
    print(len(S.S))
