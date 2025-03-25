from networkx import Graph
from typing import Set
import os


def read_graph(file_name: str) -> Graph:
    g = Graph()
    with open(file_name, "r") as file:
        if os.path.splitext(file_name)[1] == ".graph":
            g = _read_test_instance(file)

        if os.path.splitext(file_name)[1] == ".txt":
            g = _read_city_instance(file)

    return g


def _read_test_instance(file) -> Graph:
    graph = Graph()

    edges = []
    for line in file.readlines():
        currentLine = [_ for _ in line.strip().split(" ")]

        if currentLine[0] == "c":
            continue

        if currentLine[0] == "p":
            graph.add_nodes_from(range(int(currentLine[-2])))
            continue

        if currentLine[0] == "e":
            u, v = currentLine[-2:]
            edges.append((int(u), int(v)))

    graph.add_edges_from(edges)

    return graph


def _read_city_instance(file) -> Graph:
    graph = Graph()
    first_line = file.readline().strip().split(" ")
    n_nodes, n_edges = [int(_) for _ in first_line]

    graph.add_nodes_from(range(n_nodes))

    edges = []
    for line in file.readlines():
        u, v = [int(_) for _ in line.strip().split(" ")]
        edges.append((u, v))

    graph.add_edges_from(edges)

    return graph


def validate_solution(G: Graph, solution_set: Set, K: int) -> bool:
    isSolutionValid = True
    for v in G.nodes():
        count_neighboor = 0

        if v in solution_set:
            continue

        for u in G[v]:
            if u in solution_set:
                count_neighboor += 1
        if count_neighboor < K:
            print(f"\n{v} has only {count_neighboor} neighboors")
            isSolutionValid = False

    return isSolutionValid
