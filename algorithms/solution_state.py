from networkx import Graph
from typing import Set, List
from algorithms.utils.graph_reader import read_graph
from enum import IntEnum
import copy


class Index(IntEnum):
    K = 0
    DEGREE = 1
    WEIGHT = 2


class SolutionState:

    def __init__(self, instance_path: str, K: int):
        self._K = K
        self._G: Graph = read_graph(instance_path)
        self._G_info: List[List[int | float]] = []
        self._S: Set[int] = set()
        self._dominated: Set[int] = set()
        self._non_dominated: Set[int] = set(self._G.nodes())

        self.__info_indexes: Set[int] = set()
        self.__initial_G_info = []

    @property
    def G(self) -> Graph:
        return self._G

    @property
    def K(self) -> int:
        return self._K

    @property
    def S(self) -> Set[int]:
        return self._S

    @property
    def non_dominated(self) -> Set[int]:
        return self._non_dominated

    @property
    def dominated(self) -> Set[int]:
        return self._dominated

    @property
    def info_indexes(self) -> Set[int]:
        return self.__info_indexes

    @property
    def G_info(self) -> List[List[int | float]]:
        return self._G_info

    @G_info.setter
    def G_info(self, updated_info: List[List[int | float]]) -> None:
        self._G_info = updated_info

    @non_dominated.setter
    def non_dominated(self, non_dominated: Set[int]) -> None:
        self._non_dominated = non_dominated

    @dominated.setter
    def dominated(self, dominated: Set[int]) -> None:
        self._dominated = dominated

    def add_info_index(self, indexes: List[Index]) -> None:
        self.__info_indexes.update(indexes)

    def is_solution_empty(self) -> bool:
        return not self._S

    def is_state_clear(self) -> bool:
        return not self._S and not self._G_info

    def reset_G_info(self):
        self.G_info = copy.deepcopy(self.__initial_G_info)

    def init_G_info(self) -> None:
        if self._G_info:
            self.reset_G_info
            return

        for node in self.G.nodes():
            node_info = [0] * len(self.__info_indexes)
            if Index.K in self.__info_indexes:
                node_info[Index.K] = self.K
            if Index.DEGREE in self.__info_indexes:
                node_info[Index.DEGREE] = self.G.degree[node]
            if Index.WEIGHT in self.__info_indexes:
                node_info[Index.WEIGHT] = 0.0

            self.G_info.append(node_info)

        self.__initial_G_info = copy.deepcopy(self.G_info)


if __name__ == "__main__":
    K = 2
    S = SolutionState("instances/test_instances/g10-50-1234.graph", K)

    for node in S.G.adj:
        neighbors = list(S.G.adj[node])
        print(f"{node}: {neighbors}")
