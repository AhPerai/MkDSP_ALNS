from abc import abstractmethod
from typing import Tuple
from algorithms.alns.enum.alns_enum import Outcome
from algorithms.solution_state import SolutionState
from algorithms.alns.reset import Resettable


class AcceptStrategy(Resettable):

    @abstractmethod
    def _accept(self, curr_S: int, new_S: int) -> bool:
        return NotImplemented

    def update_values(self) -> None:
        pass

    def evaluate_solution(
        self, best_S: SolutionState, curr_S: SolutionState, new_S: SolutionState
    ) -> Tuple[SolutionState, SolutionState, Outcome]:
        """
        Returns a Tuple with the Best Solution, Current Solution, Outcome
        """
        if len(new_S.S) < len(best_S.S):  # If new_S is the best found so far
            return (new_S.copy(), new_S.copy(), Outcome.BEST)

        if len(new_S.S) < len(curr_S.S):  # If new_S is better than curr_S
            return (best_S, new_S.copy(), Outcome.BETTER)

        if self._accept(
            len(curr_S.S), len(new_S.S)
        ):  # If accepted by Metropolis or other criterion
            return (best_S, new_S.copy(), Outcome.ACCEPTED)

        return (best_S, curr_S, Outcome.REJECTED)

    @abstractmethod
    def reset(self, rng=None):
        """Resets the acceptance strategy (abstract)"""
        pass
