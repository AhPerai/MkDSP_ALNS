from algorithms.solution_state import SolutionState, Index


def repair(current_S: SolutionState) -> SolutionState:
    G = current_S.G

    # main loop
    while len(current_S.non_dominated) > 0:
        v = next(iter(current_S.non_dominated))

        # select the vertex with maximum degree
        for u in current_S.non_dominated:
            if current_S.G_info[v][Index.K] < current_S.G_info[u][Index.K]:
                v = u

        # add the vertex to the solution
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

    S.G_info = [[S.K, S.G.degree[node]] for node in S.G.nodes()]
    # pprint.pprint(S.G_info)
    # pprint.pprint(S.non_dominated)
    S = repair(S)
    print(len(S.S))
    # pprint.pprint(S.G_info)

    # count = 0
    # for v in graph.nodes():
    #     if graph.degree[v] == 0:  # type: ignore
    #         count += 1

    # print(f"orphan nodes: {count}")

    # vis = Visualizer(graph)
    # vis.show(S)

    # print(f"\nIs Solution Valid: {validate_solution(graph, S, K)}\nSize: {len(S)}")
