from algorithms.solution_state import SolutionState, Index
import numpy.random as random


def greedy_repair(curr_S: SolutionState) -> SolutionState:
    G = curr_S.G

    # main loop
    while len(curr_S.non_dominated) > 0:
        v = next(iter(curr_S.non_dominated))

        # select the least dominated node
        for u in curr_S.non_dominated:
            if curr_S.G_info[u][Index.K] > curr_S.G_info[v][Index.K]:
                v = u

        # add the vertex to the solution
        curr_S.S.add(v)

        for u in G[v]:
            # dominate the neighboors of V
            curr_S.G_info[u][Index.K] -= 1

            # if u is dominated, discard it
            if curr_S.G_info[u][Index.K] == 0 and u not in curr_S.S:
                curr_S.dominated.add(u)
                curr_S.non_dominated.discard(u)

        curr_S.non_dominated.discard(v)

    return curr_S


def pseudo_greedy_repair(
    curr_S: SolutionState, alpha: float, rng: random.Generator = random.default_rng()
) -> SolutionState:
    G = curr_S.G

    # main loop
    while len(curr_S.non_dominated) > 0:
        candidate_nodes = {u: curr_S.G_info[u][Index.K] for u in curr_S.non_dominated}
        max_K = max(candidate_nodes.values())
        min_K = 1

        threshold = max_K - alpha * (max_K - min_K)
        RCL = [u for u, k in candidate_nodes.items() if k >= threshold]
        v = rng.choice(RCL)

        curr_S.S.add(v)

        for u in G[v]:
            # dominate the neighboors of V
            curr_S.G_info[u][Index.K] -= 1

            # if u is dominated, discard it
            if curr_S.G_info[u][Index.K] == 0 and u not in curr_S.S:
                curr_S.dominated.add(u)
                curr_S.non_dominated.discard(u)

        curr_S.non_dominated.discard(v)

    return curr_S
