from algorithms.solution_state import SolutionState, Index
import numpy.random as random


def greedy_repair(curr_S: SolutionState) -> SolutionState:
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
            if curr_S.G_info[u][Index.K] > curr_S.G_info[v][Index.K]:
                v = u
            elif curr_S.G_info[u][Index.K] == curr_S.G_info[v][Index.K]:
                if curr_S.G_info[u][Index.DEGREE] > curr_S.G_info[v][Index.DEGREE]:
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

    return curr_S


def pseudo_greedy_repair(curr_S: SolutionState, alpha: float) -> SolutionState:
    G = curr_S.G

    # main loop
    while len(curr_S.non_dominated) > 0:
        candidate_nodes = {
            u: [curr_S.G_info[u][Index.K], curr_S.G_info[u][Index.DEGREE]]
            for u in curr_S.non_dominated
        }

        max_K = max(val[Index.K] for val in candidate_nodes.values())
        min_K = 1
        max_degree = max(val[Index.DEGREE] for val in candidate_nodes.values())
        min_degree = min(val[Index.DEGREE] for val in candidate_nodes.values())

        k_threshold = max_K - alpha * (max_K - min_K)
        degree_threshold = max_degree - alpha * (max_degree - min_degree)

        RCL = [
            u
            for u, info in candidate_nodes.items()
            if info[Index.K] >= k_threshold and info[Index.DEGREE] >= degree_threshold
        ]

        v = random.choice(RCL)

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

    return curr_S


if __name__ == "__main__":
    import os

    K = 2
    INSTANCE_FOLDER = "instances/cities_small_instances"
    for filename in os.listdir(INSTANCE_FOLDER):
        city_name = filename.replace(".txt", "")
        path = os.path.join(INSTANCE_FOLDER, filename)

        S = SolutionState(path, K)
        S.add_info_index([Index.K, Index.DEGREE])
        S.init_G_info()
        S = pseudo_greedy_repair(S, 0.3)

        print(f"Instance: {city_name} | Result: {len(S.S)}")
