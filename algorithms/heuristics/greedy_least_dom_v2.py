from algorithms.solution_state import SolutionState, Index


def repair(curr_S: SolutionState) -> SolutionState:
    G = curr_S.G

    # main loop
    while len(curr_S.non_dominated) > 0:
        v = next(iter(curr_S.non_dominated))

        """
        select the vertex with maximum degree
        if U is less dominated than V accept it instantly
        if they're equal it's decided by their current degree value
        """
        for u in curr_S.non_dominated:
            if curr_S.G_info[v][Index.K] < curr_S.G_info[u][Index.K]:
                v = u
            elif curr_S.G_info[v][Index.K] == curr_S.G_info[u][Index.K]:
                if curr_S.G_info[v][Index.DEGREE] < curr_S.G_info[u][Index.DEGREE]:
                    v = u

        # add the vertex to the solution
        curr_S.S.add(v)

        for u in G[v]:
            # dominate the neighbors of V
            curr_S.G_info[u][Index.K] -= 1

            # update the node degree as the edge between them and V is no longer relevant
            if curr_S.G_info[u][Index.DEGREE] > 0:
                curr_S.G_info[u][Index.DEGREE] -= 1

            # when fully dominating u, update the node degree between u and its neightboors, as u is no longer relevant
            if curr_S.G_info[u][Index.K] == 0 and u not in curr_S.S:
                curr_S.dominated.add(u)
                curr_S.non_dominated.discard(u)
                for w in G[u]:
                    # update the node degree as the edge between U and W is no longer relevant
                    if curr_S.G_info[w][Index.DEGREE] > 0:
                        curr_S.G_info[w][Index.DEGREE] -= 1

        curr_S.non_dominated.discard(v)

    return S


if __name__ == "__main__":
    K = 2
    S = SolutionState("instances/cities_small_instances/belfast.txt", K)
    print(f"Solution initialized: {S.is_state_clear()}")
    S.G_info = [[S.K, S.G.degree[node]] for node in S.G.nodes()]
    S = repair(S)
    print(len(S.S))
