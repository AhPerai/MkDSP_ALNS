from algorithms.alns.operators.operator_strategy import (
    OperatorStrategy,
    OperatorContext,
)
from algorithms.solution_state import SolutionState, Index
from algorithms.heuristics.greedy_degree import pseudo_greedy_repair
import numpy.random as random


class GreedyDegreeOperator(OperatorStrategy):
    name = "remaining_neighbors_repair"

    def __init__(
        self,
        greedy_alpha: float,
        rng: random.Generator = random.default_rng(),
    ):
        super().__init__()
        if not (0 <= greedy_alpha <= 1):
            raise ValueError("Must be a float equal or between 0 and 1")
        self._rng = rng
        self._alpha = greedy_alpha
        self._info_indexes.append(Index.DEGREE)

    @classmethod
    def get_instance_from_context(cls, context: OperatorContext):
        return cls(context.greedy_alpha, context.rng)

    def reset(self, rng=None):
        self._rng = rng

    def _modify_solution(self, curr_S: SolutionState) -> SolutionState:
        return pseudo_greedy_repair(curr_S, self._alpha, self._rng)

    def _update_state_info(self, curr_S: SolutionState) -> SolutionState:
        if curr_S.is_solution_empty():
            curr_S.reset_G_info()
            return curr_S

        for v in curr_S.non_dominated:
            for u in curr_S.G[v]:
                curr_S.G_info[u][Index.DEGREE] += 1

        return curr_S


if __name__ == "__main__":
    import numpy.random as random
    from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
    from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy
    from algorithms.utils.debug_functions import debug_state_difference
    from tests.utils.state_info_assertions import init_state_k_degree

    # Configuration parameters
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/york.txt"
    DESTROY_FACTOR = 0.5
    SEED = 1234
    GREEDY_ALPHA = 0.3
    # Create the initial solution state
    S = SolutionState(INSTANCE_PATH, K)
    rng = random.default_rng(SEED)

    # Initialing operators
    random_repair_op = RandomRepair(rng)
    main_operator = GreedyDegreeOperator(GREEDY_ALPHA)
    destroy_op = RandomDestroy(DESTROY_FACTOR, rng)

    main_operator.init_state_info(S)
    S = main_operator.operate(S)

    # Run the cycle for N iterations
    for i in range(100):
        # Step 1: Destroy part of the solution
        S_destroyed = destroy_op.operate(S)  # Step 1: Destroy some nodes

        if rng.random() < 0.7:
            # Step 2a: Update state manually
            S_updated = main_operator._update_state_info(S_destroyed)
            S_expected = init_state_k_degree(S_destroyed)

            # Compare both ways of building the state
            debug_state_difference(
                S_updated, S_expected, i, SEED, [Index.K, Index.DEGREE]
            )

            # Step 2b: Reconstruct with the repair operator
            S_modified = main_operator._modify_solution(S_updated)
            S_expected = init_state_k_degree(S_modified)

            # Validate again
            debug_state_difference(
                S_modified, S_expected, i, SEED, [Index.K, Index.DEGREE]
            )
        else:
            # Use a different operator
            S_updated = random_repair_op.operate(S_destroyed)

        S = S_updated
