from algorithms.solution_state import SolutionState, Index
import numpy.random as random


def calc_weight(dom_value: int, degree: int, n_nodes: int) -> float:
    factor: float = (dom_value * dom_value) / (n_nodes - degree)
    return factor


def greedy_repair(current_S: SolutionState) -> SolutionState:
    G = current_S.G

    while len(current_S.non_dominated) > 0:
        v = next(iter(current_S.non_dominated))

        if len(current_S.non_dominated) > 0:
            for u in current_S.non_dominated:
                current_S.G_info[u][Index.WEIGHT] = calc_weight(
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


def pseudo_greedy_repair(current_S: SolutionState, alpha: float) -> SolutionState:
    G = current_S.G

    while len(current_S.non_dominated) > 0:

        candidate_nodes = {}
        for u in current_S.non_dominated:
            candidate_nodes[u] = current_S.G_info[u][Index.WEIGHT] = calc_weight(
                int(current_S.G_info[u][Index.K]),
                int(current_S.G_info[u][Index.DEGREE]),
                len(current_S.non_dominated),
            )

        max_weight = max(candidate_nodes.values())
        min_weight = min(candidate_nodes.values())

        threshold = max_weight - alpha * (max_weight - min_weight)
        RCL = [u for u, w in candidate_nodes.items() if w >= threshold]

        v = random.choice(RCL)

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
    import os

    K = 2
    INSTANCE_FOLDER = "instances/cities_small_instances"
    for filename in os.listdir(INSTANCE_FOLDER):
        city_name = filename.replace(".txt", "")
        path = os.path.join(INSTANCE_FOLDER, filename)

        S = SolutionState(path, K)
        S.add_info_index([Index.K, Index.DEGREE, Index.WEIGHT])
        S.init_G_info()
        S = pseudo_greedy_repair(S, 0.3)

        print(f"Instance: {city_name} | Result: {len(S.S)}")
