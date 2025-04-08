from networkx import Graph
from typing import Set, List
from algorithms.utils.graph_reader import read_graph


class SolutionState:

    def __init__(self, instance: str, K: int = None):
        self._G: Graph = read_graph(instance)
        self._S: Set[int] = set()
        self._dominated: Set[int] = set()
        self._non_dominated: Set[int] = set(self._G.nodes())
        self._G_info: List[List[int | float]] = []
        if K is not None:
            self.init_G_info(K)

    @property
    def G(self) -> Graph:
        return self._G

    @property
    def current_S(self) -> Set[int]:
        return self._S

    @property
    def non_dominated(self) -> Set[int]:
        return self._non_dominated

    @property
    def dominated(self) -> Set[int]:
        return self._dominated

    @property
    def G_info(self) -> List[List[int | float]]:
        return self._G_info

    def init_G_info(self, K: int):
        self._G_info = [[node, K] for node in self._G.nodes()]

    def update_G_info(self, operator):
        pass

    def is_solution_empty(self) -> bool:
        return not self._S
