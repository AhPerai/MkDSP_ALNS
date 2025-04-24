from algorithms.solution_state import SolutionState, Index


def repair(current_S: SolutionState) -> SolutionState:
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


import os

if __name__ == "__main__":
    K = 2
    INSTANCE_FOLDER = "instances/cities_small_instances"

    for filename in os.listdir(INSTANCE_FOLDER):
        city_name = filename.replace(".txt", "")
        path = os.path.join(INSTANCE_FOLDER, filename)

        S = SolutionState(path, K)
        S.add_info_index([Index.K, Index.DEGREE])
        S.init_G_info()
        S = repair(S)

        print(f"Instance: {city_name} | Result: {len(S.S)}")

        # K = 2
        # CITY = "belfast"
        # PATH = "instances/cities_small_instances/{CITY}.txt"
        # S = SolutionState("instances/cities_small_instances/belfast.txt", K)
        # S.add_info_index([Index.K, Index.DEGREE])
        # S.init_G_info()
        # S = repair(S)
        # print(f"Instance: {CITY} | Result: {len(S.S)}")
