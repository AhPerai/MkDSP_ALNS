from abc import ABC, abstractmethod
from typing import Tuple
from alns.outcome import Outcome
from networkx import Graph


class AcceptStrategy(ABC):

    @abstractmethod
    def _accept(self, best_S: Graph, curr_S: Graph, new_S: Graph) -> bool:
        return NotImplemented

    def evaluate_solution(
        self, best_S: Graph, curr_S: Graph, new_S: Graph
    ) -> Tuple[Graph, Graph, Outcome]:
        return (best_S, curr_S, Outcome.REJECTED)
