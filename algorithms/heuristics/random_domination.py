from algorithms.solution_state import SolutionState, Index
import numpy.random as random


def repair(
    current_S: SolutionState, rng: random.Generator = random.default_rng()
) -> SolutionState:
    G = current_S.G

    # main loop
    while len(current_S.non_dominated) > 0:
        v = rng.choice(list(current_S.non_dominated))

        # add the vertex to the solution
        current_S.S.add(v)

        for u in G[v]:

            # dominate the neighbors of V
            current_S.G_info[u][Index.K] -= 1

            # discard u
            if current_S.G_info[u][Index.K] == 0 and u not in current_S.S:
                current_S.dominated.add(u)
                current_S.non_dominated.discard(u)

        current_S.non_dominated.discard(v)

    return current_S


if __name__ == "__main__":
    K = 2
    S = SolutionState("instances/cities_small_instances/belfast.txt", K)
    S.G_info = [[S.K, S.G.degree[node]] for node in S.G.nodes()]
    S = repair(S)
    print(len(S.S))
