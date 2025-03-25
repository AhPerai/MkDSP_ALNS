import networkx as nx
import numpy as np
from pyvis.network import Network


class Visualizer:
    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def print_as_adjmatrix(self):
        print("Adjacency Matrix:")
        print(nx.to_numpy_array(self.graph))

    def print_as_adjlist(self):
        print("Adjacency List:")
        adj_list = nx.to_dict_of_lists(self.graph)
        for node, neighbors in adj_list.items():
            print(f"{node}: {neighbors}")

    def show(self, solution_set = None):
        # pos = nx.circular_layout(self.graph,scale=500)
        network = Network()
        network.from_nx(self.graph)

        adj_list = network.get_adj_list()

        for node in network.nodes: 
            # network.get_node(node['id'])['physics']=False
            node['label'] = f'{node['id']}'
            node['value'] = len(adj_list[node['id']])
            node['color'] = 'lightblue'

            if solution_set and node['id'] in solution_set:
                node['color'] = 'red'

        if solution_set:
            for edge in network.edges:
                source = edge['from']
                target = edge['to']

                if source in solution_set or target in solution_set:
                    edge['color'] = 'red'           
         
        # network.toggle_physics(False)
        network.set_edge_smooth('straight')
        network.show_buttons(filter_=['physics'])
        network.show("graph.html", notebook=False)
