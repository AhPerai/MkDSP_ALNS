from abc import ABC, abstractmethod
from networkx import Graph


class IOperatorStrategy(ABC):

    def __init__(self, name: str, K: int):
        self._name = name
        self._K = K

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def operate(self, current_solution: Graph) -> Graph:
        return NotImplemented
