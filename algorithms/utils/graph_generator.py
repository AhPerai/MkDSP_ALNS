import sys
from datetime import datetime
import random

num_vertices = int(sys.argv[1])
probability = float(sys.argv[2])
seed = int(sys.argv[3])
folder_path = f"instances\\test_instances"

random.seed(seed)
filename = f"g{num_vertices}-{int(probability * 100)}-{seed}.graph"

content = f"c FILE: {filename}\n"
content += "c\n"
content += f"c DESCRIPTION: This is a random graph with {num_vertices} vertices.\n"
content += f"c   Each of pair of vertices are made adjacent with probability p = {probability}.\n"
content += f"c   The random seed used for its generation was {seed}.\n"
content += "c\n"
content += f'c {datetime.now().strftime("%d/%m/%Y")}\n'
content += "c\n"

edges = ""
num_edges = 0
edges_create = {}

vertices = [x for x in range(num_vertices)]
random.shuffle(vertices)
for i in range(len(vertices) - 1):
    vertex_from = min(vertices[i], vertices[i + 1])
    vertex_to = max(vertices[i], vertices[i + 1])
    edges_create[vertex_from] = vertex_to

for v in vertices:
    if v not in edges_create:
        edges_create[v] = None

for i in range(num_vertices):
    for j in range(i + 1, num_vertices):
        if edges_create[i] == j or random.random() <= probability:
            edges += f"e {i} {j}\n"
            num_edges += 1

content += f"p edge {num_vertices} {num_edges}\n"
content += edges[:-1]

with open(f"{folder_path}\\{filename}", "w") as f:
    f.write(content)
