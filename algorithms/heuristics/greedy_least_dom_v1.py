from algorithms.solution_state import SolutionState, Index


def repair(curr_S: SolutionState) -> SolutionState:
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
