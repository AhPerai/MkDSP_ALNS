from abc import ABC, abstractmethod
from typing import Tuple
from algorithms.alns.outcome import Outcome
from networkx import Graph


class AcceptStrategy(ABC):

    @abstractmethod
    def _accept(self, curr_S: Graph, new_S: Graph) -> bool:
        return NotImplemented

    def update_values(self) -> None:
        pass

    def evaluate_solution(
        self, best_S: Graph, curr_S: Graph, new_S: Graph
    ) -> Tuple[Graph, Graph, Outcome]:
        """
        Returns a Tuple with the Best Solution, Current Solution, Outcome
        """
        if len(new_S) < len(best_S):  # If new_S is the best found so far
            return (new_S, new_S, Outcome.BEST)

        if len(new_S) < len(curr_S):  # If new_S is better than curr_S
            return (best_S, new_S, Outcome.BETTER)

        # If accepted by Metropolis criterion (or any other criteria that may be implemented in the future)
        if self._accept(len(curr_S), len(new_S)):
            return (best_S, new_S, Outcome.ACCEPTED)

        return (best_S, curr_S, Outcome.REJECTED)
