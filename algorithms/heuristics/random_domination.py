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


import os

if __name__ == "__main__":
    K = 2
    INSTANCE_FOLDER = "instances/cities_small_instances"
    for filename in os.listdir(INSTANCE_FOLDER):
        city_name = filename.replace(".txt", "")
        path = os.path.join(INSTANCE_FOLDER, filename)

        S = SolutionState(path, K)
        S.add_info_index([Index.K])
        S.init_G_info()
        S = repair(S)

        print(f"Instance: {city_name} | Result: {len(S.S)}")
