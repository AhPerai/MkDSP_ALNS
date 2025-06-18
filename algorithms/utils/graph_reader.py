from networkx import Graph
import os
import pickle
from corcoran2021.street_network_env import street_network_env


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


def convert_pickle_to_txt(input_folder, output_folder):
    """
    Recupera os arquivos .pickle disponibilizados por CORCORAN e os transforma em txt
    O grafo que é transformado é o reachability network (rn)
    No fim reordena os indexes OSM para números contínuos 0..n-1
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith("_pickle"):
            continue

        city = filename.replace("_pickle", "")
        file_path = os.path.join(input_folder, filename)
        print(f"Processing {file_path}...")

        with open(file_path, "rb") as f:
            env_obj = pickle.load(f)

        rn_graph = env_obj.rn

        # Reordena os indices
        osmid_to_idx = {}
        nodes = list(rn_graph.nodes)
        for idx, osmid in enumerate(nodes):
            osmid_to_idx[osmid] = idx

        # Escreve o txt com os indices reornados na parte de arestas
        out_file = os.path.join(output_folder, f"{city}.txt")
        with open(out_file, "w") as out:
            n_nodes = len(nodes)
            n_edges = rn_graph.number_of_edges()
            out.write(f"{n_nodes} {n_edges}\n")
            for u, v in rn_graph.edges():
                out.write(f"{osmid_to_idx[u]} {osmid_to_idx[v]}\n")

        print(f"Convertido {out_file}")

    print("Conversão concluida!")
