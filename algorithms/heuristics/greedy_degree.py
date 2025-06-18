from algorithms.solution_state import SolutionState, Index
import numpy.random as random


def greedy_repair(current_S: SolutionState) -> SolutionState:
    G = current_S.G

    # main loop
    while len(current_S.non_dominated) > 0:
        v = next(iter(current_S.non_dominated))

        # select the vertex with maximum degree
        for u in current_S.non_dominated:
            if current_S.G_info[u][Index.DEGREE] > current_S.G_info[v][Index.DEGREE]:
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


def pseudo_greedy_repair(
    current_S: SolutionState, alpha: float, rng: random.Generator = random.default_rng()
):
    G = current_S.G

    while len(current_S.non_dominated) > 0:
        candidate_nodes = {
            u: current_S.G_info[u][Index.DEGREE] for u in current_S.non_dominated
        }
        max_degree = max(candidate_nodes.values())
        min_degree = min(candidate_nodes.values())

        threshold = max_degree - alpha * (max_degree - min_degree)
        RCL = [u for u, degree in candidate_nodes.items() if degree >= threshold]

        v = rng.choice(RCL)

        current_S.S.add(v)

        for u in G[v]:
            current_S.G_info[u][Index.K] -= 1

            if current_S.G_info[u][Index.DEGREE] > 0:
                current_S.G_info[u][Index.DEGREE] -= 1

            if current_S.G_info[u][Index.K] == 0 and u not in current_S.S:
                current_S.dominated.add(u)
                current_S.non_dominated.discard(u)
                for w in G[u]:
                    if current_S.G_info[w][Index.DEGREE] > 0:
                        current_S.G_info[w][Index.DEGREE] -= 1

        current_S.non_dominated.discard(v)

    return current_S
