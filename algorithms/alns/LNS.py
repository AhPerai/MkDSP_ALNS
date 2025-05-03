import numpy as np

from algorithms.solution_state import SolutionState, Index
from algorithms.alns.acept_criterion.accept_strategy import AcceptStrategy
from algorithms.alns.stop.stop_condition import StopCondition
from algorithms.alns.operators.operator_strategy import OperatorStrategy

from algorithms.alns.event_handler import Event, EventHandler
from algorithms.alns.statistics import Statistics

from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy

from algorithms.alns.stop.stop_condition import Interrupt


class LNS:

    def __init__(
        self,
        stop: StopCondition,
        accept: AcceptStrategy,
        events: EventHandler = EventHandler(),
        rng: np.random.Generator = np.random.default_rng(),
        track_stats: bool = False,
    ):
        self._rng = rng
        self._stop = stop
        self._accept = accept
        self._events = events
        self._stats = None
        self._track_stats = track_stats

        self._destroy_operator: OperatorStrategy = None
        self._repair_operator: OperatorStrategy = None

    @property
    def events(self):
        return self._events

    @property
    def stats(self):
        return self._stats

    @property
    def stop(self):
        return self._stop

    @property
    def repair_operator(self):
        return self._repair_operator

    @property
    def destroy_operator(self):
        return self._destroy_operator

    @repair_operator.setter
    def repair_operator(self, repair_operator: OperatorStrategy) -> None:
        self._repair_operator = repair_operator

    @destroy_operator.setter
    def destroy_operator(self, destroy_operator: OperatorStrategy) -> None:
        self._destroy_operator = destroy_operator

    @property
    def n_repair_operators(self) -> int:
        return 1 if self._repair_operator is not None else 0

    @property
    def n_destroy_operators(self) -> int:
        return 1 if self._destroy_operator is not None else 0

    def setup(self, initial_S: SolutionState):
        self._stop.init_time()

        operators_list = [self._destroy_operator, self._repair_operator]
        for operator in operators_list:
            initial_S.add_info_index(operator.info_indexes)
        initial_S.init_G_info()

        initial_repair_operator = RandomRepair(self._rng)
        initial_repair_operator.operate(initial_S)
        # quick bug fix
        if Index.DEGREE in initial_S.info_indexes:
            for node in initial_S.G.nodes():
                initial_S.G_info[node][Index.DEGREE] = 0

        if self._track_stats:
            self._stats = Statistics(self)
            self.stats.add_basic_data_tracker()

    def validate(self):
        if self.n_destroy_operators == 0 or self.n_repair_operators == 0:
            raise ValueError("No repair or destroy operators found")

    def execute(self, initial_S) -> SolutionState:
        self.validate()
        self.setup(initial_S)

        curr_S = initial_S.copy()
        best_S = initial_S.copy()

        while not self._stop.stop():
            d_operator = self._destroy_operator
            r_operator = self._repair_operator

            destroyed_S = d_operator.operate(curr_S.copy())
            new_S = r_operator.operate(destroyed_S)

            best_S, curr_S, outcome = self._accept.evaluate_solution(
                best_S, curr_S, new_S
            )
            self._events.on_outcome(outcome, new_S, self.repair_operator.name)
            print(f"new solution value: {len(new_S.S)} outcome:{outcome}")

        self._events.trigger(Event.ON_END)
        return best_S


if __name__ == "__main__":
    from algorithms.alns.operators.repair_operators.greedy_least_dom import (
        GreedyLeastDominatedOperator,
    )
    from algorithms.alns.acept_criterion.simulated_annealing import SimulatedAnnealing

    #  fixed variables
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/leeds.txt"
    SEED = 5432
    GREEDY_ALPHA = 0.3
    DESTROY_FACTOR = 0.5
    rng = np.random.default_rng(SEED)

    # stop condition
    stop_by_iterations = StopCondition(Interrupt.BY_ITERATION_LIMIT, 1000)
    # acceptance criterion
    simulated_annealing = SimulatedAnnealing(10, 2, 0.95, rng)

    # initializing LNS
    lns = LNS(
        stop=stop_by_iterations,
        accept=simulated_annealing,
        rng=rng,
        track_stats=True,
    )

    # repair
    lns.repair_operator = GreedyLeastDominatedOperator(GREEDY_ALPHA)
    # destroy
    lns.destroy_operator = RandomDestroy(DESTROY_FACTOR, rng)

    results = []
    # for _ in range(10):
    # alns.randomize_rng()

    initial_S = SolutionState(INSTANCE_PATH, K)
    best_solution = lns.execute(initial_S)
    results.append(len(best_solution.S))

    best = min(results)
    avg = np.mean(results)
    std = np.std(results)
    import pprint

    print(f"0. runtime duration: {lns.stats.get_runtime_duration()}")

    print("3. Tracking Best Solution\n")
    pprint.pprint(lns.stats.best_solution_tracking)

    print("\n4. Last Best Solution")
    print(lns.stats.get_last_time_to_best())
    print(f"Instance: {INSTANCE_PATH} | Best: {best} | Avg: {avg:.2f} | Std: {std:.2f}")
