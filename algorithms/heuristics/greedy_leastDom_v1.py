from algorithms.utils.graph_reader import read_graph, validate_solution
from algorithms.utils.graph_visualizer import Visualizer
from typing import Dict, Set, List
from networkx import Graph


def generate_solution(graph: Graph, K):
    G = graph

    """
    non_dominated = G.nodes; its a Set containing only the nodes' id
    G_info is a dict where key = node_id -> [K_value]
    S is the solution set
    """
    G_info: Dict[int, List[int]] = dict()
    non_dominated: Set[int] = set()
    S: Set[int] = set()

    for v in G.nodes():
        G_info[v] = [K, G.degree[v]]  # type: ignore
        non_dominated.add(v)

    # main loop
    while len(non_dominated) > 0:
        v = next(iter(non_dominated))

        # select the vertex with maximum degree
        for u in non_dominated:
            if G_info[v][0] < G_info[u][0]:
                v = u
            elif G_info[v][0] == G_info[u][0]:
                if G_info[v][1] < G_info[u][1]:
                    v = u

        # add the vertex to the solution
        S.add(v)

        for neighbor in G[v]:

            # dominate the neighbors of V
            if G_info[neighbor][0] > 0:
                G_info[neighbor][0] -= 1

            # update the node degree as the edge between them and V is no longer relevant
            if G_info[u][1] > 0:
                G_info[u][1] -= 1

            if G_info[neighbor][0] == 0:
                non_dominated.discard(neighbor)
                for w in G[neighbor]:
                    if G_info[w][1] > 0:
                        G_info[w][1] -= 1

        non_dominated.discard(v)

    return S


if __name__ == "__main__":
    K = 460
    graph = read_graph("instances/cities_small_instances/bath.txt")
    graph = read_graph("instances/test_instances/g2000-50-42.graph")
    # print(f"edge number: {graph.number_of_edges()}")
    S = generate_solution(graph, K)

    # count = 0
    # for v in graph.nodes():
    #     if graph.degree[v] == 0:  # type: ignore
    #         count += 1

    # print(f"orphan nodes: {count}")

    print(f"\nIs Solution Valid: {validate_solution(graph, S, K)}\nSize: {len(S)}")

    # vis = Visualizer(graph)
    # vis.show(S)
