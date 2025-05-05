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

        self._events.trigger(Event.ON_END)
        return best_S


from algorithms.alns.operators.repair_operators.greedy_least_dom import (
    GreedyLeastDominatedOperator,
)
from algorithms.alns.acept_criterion.simulated_annealing import SimulatedAnnealing


def run_LNS(K, path):
    #  fixed variables
    GREEDY_ALPHA = 0.1
    DESTROY_FACTOR = 0.5
    ITERATION = 10
    rng = np.random.default_rng()

    # stop condition
    stop_by_iterations = StopCondition(Interrupt.BY_ITERATION_LIMIT, ITERATION)
    # acceptance criterion
    simulated_annealing = SimulatedAnnealing(10, 1, 0.99, rng)

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

    initial_S = SolutionState(path, K)
    best_solution = lns.execute(initial_S)
    return {
        "ObjValue": len(best_solution.S),
        "TimeToBest": lns.stats.get_last_time_to_best(),
        "Runtime": lns.stats.get_runtime_duration(),
    }


def run_for_instance(instance_path, K, i):
    results = []
    for _ in range(i):
        stats = run_LNS(K, instance_path)
        results.append(stats)

    print("\n === RESULTS ===")
    solution_sizes = [res["ObjValue"] for res in results]
    ttb_time = [res["TimeToBest"][2] for res in results]
    ttb_iteration = [res["TimeToBest"][1] for res in results]
    runtime = [res["Runtime"] for res in results]

    import pprint

    for result in results:
        pprint.pprint(
            f"Solution Value: {result["ObjValue"]} | TtB: (Time: {result["TimeToBest"][2]:.2f} | Iteration: {result["TimeToBest"][1]:.0f}) | RunTime: {result["Runtime"]:.2f}"
        )

    best = min(solution_sizes)
    avg = np.mean(solution_sizes)
    std = np.std(solution_sizes)

    avg_time = np.mean(runtime)
    avg_time_ttb = np.mean(ttb_time)
    avg_iteration_ttb = np.mean(ttb_iteration)

    filename = INSTANCE_PATH.split("/")[-1]
    CITY_NAME = filename.split(".")[0]
    print(
        f"\n === MEANS === \nInstance: {CITY_NAME} | Best: {best} | Avg: {avg:.2f} | Std: {std:.2f}\nAvg_Time: {avg_time:.2f} | Avg_Time_To_Bet: {avg_time_ttb:.2f} | Avg_Time_To_Best_IT: {avg_iteration_ttb:.0f}"
    )


import os

if __name__ == "__main__":
    K = 2
    INSTANCE_FOLDER = "instances/cities_small_instances"
    NUM_RUNS = 5

    results = {}

    for filename in os.listdir(INSTANCE_FOLDER):
        if filename.endswith(".txt"):
            instance_path = os.path.join(INSTANCE_FOLDER, filename)
            instance_results = []

            for _ in range(NUM_RUNS):
                stats = run_LNS(K, instance_path)
                instance_results.append(stats)

            results[filename] = instance_results

    for instance, runs in results.items():
        print(f"\nResults for {instance}:")
        for i, run in enumerate(runs, 1):
            print(f"  Run {i}: {run}")
