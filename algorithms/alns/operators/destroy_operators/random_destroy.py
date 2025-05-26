from algorithms.alns.operators.operator_strategy import (
    OperatorStrategy,
    OperatorContext,
)
from algorithms.solution_state import SolutionState, Index
import numpy.random as random
import math


class RandomDestroy(OperatorStrategy):
    name = "random_destroy"

    def __init__(
        self,
        destroy_factor: float,
        rng: random.Generator = random.default_rng(),
    ):
        super().__init__()
        if not (0 < destroy_factor < 1):
            raise ValueError("Destroy factor must be greater than 0 and lower than 1")
        self._destroy_factor = destroy_factor
        self._rng = rng

    @property
    def destroy_factor(self) -> str:
        return self._destroy_factor

    @classmethod
    def get_instance_from_context(cls, context: OperatorContext):
        return cls(context.destroy_factor, context.rng)

    def reset(self, rng=None):
        self._rng = rng

    def _modify_solution(self, current_solution) -> SolutionState:
        remove_size = math.floor(self._destroy_factor * len(current_solution.S))
        to_remove = self._rng.choice(
            list(current_solution.S), size=remove_size, replace=False
        )

        # remove nodes that are part of the current solution
        for v in to_remove:
            # when V is removed its checked if V has been dominated by other nodes, if K > 0 it's not dominated
            current_solution.S.remove(v)

            if current_solution.G_info[v][Index.K] > 0:
                current_solution.non_dominated.add(v)
            else:
                current_solution.dominated.add(v)

            # un-dominate V's neighboors
            for u in current_solution.G[v]:

                if current_solution.G_info[u][Index.K] < current_solution.K:
                    current_solution.G_info[u][Index.K] += 1

                # if U's K-value is greater than 0 and is not part of the solution is
                if (
                    current_solution.G_info[u][Index.K] > 0
                    and u not in current_solution.S
                ):
                    current_solution.dominated.discard(u)
                    current_solution.non_dominated.add(u)

        return current_solution

    def _update_state_info(self, current_solution):
        pass
