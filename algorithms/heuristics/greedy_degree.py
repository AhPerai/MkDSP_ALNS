from algorithms.utils.graph_reader import read_graph, validate_solution
from typing import Dict, Set, List
from networkx import Graph
from algorithms.utils.graph_visualizer import Visualizer


def repair(graph: Graph, K, previous_S: Set[int] = None) -> Set[int]:
    G = graph

    """
    non_dominated = G.nodes; its a Set containing only the nodes' id
    G_info is a dict where: node_id -> [node_degree, K_value]
    S is the solution set
    """
    G_info: Dict[int, List[int]] = dict()
    non_dominated: Set[int] = set()
    S: Set[int] = set() if previous_S == None else previous_S

    for v in G.nodes():
        G_info[v] = [G.degree[v], K]  # type: ignore
        non_dominated.add(v)

    # main loop
    while len(non_dominated) > 0:
        v = next(iter(non_dominated))

        # select the vertex with maximum degree
        for u in non_dominated:
            if G_info[v][0] < G_info[u][0]:
                v = u

        # add the vertex to the solution
        S.add(v)

        for u in G[v]:

            # dominate the neighbors of V
            if G_info[u][1] > 0:
                G_info[u][1] -= 1

            # update the node degree as the edge between them and V is no longer relevant
            if G_info[u][0] > 0:
                G_info[u][0] -= 1

            # discard u, update the node degree between u and its neightboors, as u is no longer relevant
            if G_info[u][1] == 0:
                non_dominated.discard(u)
                for w in G[u]:
                    if G_info[w][0] > 0:
                        G_info[w][0] -= 1

        non_dominated.discard(v)

    return S


if __name__ == "__main__":
    K = 2
    graph = read_graph("instances/test_instances/g10-50-1234.graph")
    S = repair(graph, K, {5})
    print(S)

    # count = 0
    # for v in graph.nodes():
    #     if graph.degree[v] == 0:  # type: ignore
    #         count += 1

    # print(f"orphan nodes: {count}")

    # vis = Visualizer(graph)
    # vis.show(S)

    print(f"\nIs Solution Valid: {validate_solution(graph, S, K)}\nSize: {len(S)}")
