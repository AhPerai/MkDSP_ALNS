from algorithms.utils.graph_reader import read_graph, validate_solution
from algorithms.utils.graph_visualizer import Visualizer
from typing import Dict, Set, List
from networkx import Graph


def _calc_factor(dom_value: int, degree: int, n_nodes: int) -> float:
    factor: float = (dom_value * dom_value) / (n_nodes - degree)
    return factor


def repair(graph: Graph, K) -> Set[int]:
    G = graph

    """
    non_dominated = G.nodes; its a Set containing only the nodes' id
    G_info is a dict where key = node_id -> [node_degree, K_value, V_factor] | V_factor is determined by _calc_factor
    S is the solution set
    """
    G_info: Dict[int, List[int | float]] = dict()
    non_dominated: Set[int] = set()
    S: Set[int] = set()

    # G_info = node_id -> [node_degree, K_value, V_factor]
    for v in G.nodes():
        G_info[v] = [G.degree[v], K, 0]  # type: ignore
        non_dominated.add(v)

    while len(non_dominated) > 0:
        v = next(iter(non_dominated))

        if len(non_dominated) > 0:
            for u in non_dominated:
                G_info[u][2] = _calc_factor(
                    int(G_info[u][1]),
                    int(G_info[u][0]),
                    len(non_dominated),
                )
                if G_info[u][2] > G_info[v][2]:
                    v = u

        S.add(v)

        for neighbor in G[v]:
            # update the node degree as the edge between them and V is no longer relevant
            if G_info[neighbor][1] > 0:
                G_info[neighbor][1] -= 1
            # dominate the neighbors of V
            if G_info[neighbor][0] > 0:
                G_info[neighbor][0] -= 1

            if G_info[neighbor][1] == 0:
                non_dominated.discard(neighbor)
                for w in G[neighbor]:
                    if G_info[w][0] > 0:
                        G_info[w][0] -= 1

        non_dominated.discard(v)

    return S


if __name__ == "__main__":
    K = 2
    # graph = read_graph("instances/test_instances/g2000-50-42.graph")
    graph = read_graph("instances/cities_small_instances/belfast.txt")
    # print(f"edge number: {graph.number_of_edges()}")
    S = repair(graph, K)

    # count = 0
    # for v in graph.nodes():
    #     if graph.degree[v] == 0:  # type: ignore
    #         count += 1

    # print(f"orphan nodes: {count}")

    print(f"\nIs Solution Valid: {validate_solution(graph, S, K)}\nSize: {len(S)}")

    # vis = Visualizer(graph)
    # vis.show(S)
