from algorithms.solution_state import SolutionState, Index
import numpy.random as random

from algorithms.utils.graph_reader import validate_solution


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

    print(f"Is Solution Valid: {validate_solution(S.G, S.S, K)}")
