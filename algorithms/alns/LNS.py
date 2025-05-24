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
    def events(self) -> EventHandler:
        return self._events

    @property
    def stats(self) -> Statistics:
        return self._stats

    @property
    def stop(self) -> StopCondition:
        return self._stop

    @property
    def accept(self) -> AcceptStrategy:
        return self._accept

    @property
    def rng(self) -> np.random.Generator:
        return self._rng

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

    def reset(self, rng=None):
        """
        Resets all the components of ALNS to have a fresh start at a new execution
        """
        self.rng = rng
        self.stop.reset()
        self.accept.reset(rng)
        self.events.unregister_all()
        self.stats = None  # making sure cyclical reference doesnt hold on to memory


from algorithms.alns.operators.repair_operators.greedy_hybrid_degree import (
    GreedyHybridDegreeOperator,
)
from algorithms.alns.acept_criterion.simulated_annealing import SimulatedAnnealing


def run_LNS(K, path):
    #  fixed variables
    GREEDY_ALPHA = 0.25
    DESTROY_FACTOR = 0.5
    ITERATION = 5000
    rng = np.random.default_rng()

    # stop condition
    stop_by_iterations = StopCondition(Interrupt.BY_ITERATION_LIMIT, ITERATION)
    # acceptance criterion
    simulated_annealing = SimulatedAnnealing(50, 1, 0.998, rng)

    # initializing LNS
    lns = LNS(
        stop=stop_by_iterations,
        accept=simulated_annealing,
        rng=rng,
        track_stats=True,
    )

    # repair
    lns.repair_operator = GreedyHybridDegreeOperator(GREEDY_ALPHA)
    # destroy
    lns.destroy_operator = RandomDestroy(DESTROY_FACTOR, rng)

    initial_S = SolutionState(path, K)
    best_solution = lns.execute(initial_S)

    TimeToBest = lns.stats.get_last_time_to_best()
    Runtime = lns.stats.get_runtime_duration()
    lns.events.unregister_all()
    lns._stats = None
    return {
        "ObjValue": len(best_solution.S),
        "TimeToBest": TimeToBest,
        "Runtime": Runtime,
    }


if __name__ == "__main__":
    K = 2
    INSTANCE_FOLDER = "instances/cities_small_instances"
    NUM_RUNS = 3

    cities_1 = [
        "bath.txt",
        "belfast.txt",
        "brighton.txt",
        "bristol.txt",
        "cardiff.txt",
        "coventry.txt",
        "exeter.txt",
        "glasgow.txt",
        "leeds.txt",
        "leicester.txt",
        "liverpool.txt",
        "manchester.txt",
        "newcastle.txt",
        "nottingham.txt",
        "oxford.txt",
        "plymouth.txt",
        "sheffield.txt",
        "southampton.txt",
        "sunderland.txt",
        "york.txt",
    ]

    results = {}

    for filename in cities_1:
        if filename.endswith(".txt"):
            instance_path = os.path.join(INSTANCE_FOLDER, filename)
            instance_results = []

            for _ in range(NUM_RUNS):
                stats = run_LNS(K, instance_path)
                instance_results.append(stats)
                print(
                    f"finished:{filename} result:{stats["ObjValue"]}, duration: {stats["Runtime"]}"
                )

            results[filename] = instance_results

    for instance, runs in results.items():
        print(f"\n======== {instance} ========")
        solution_values = []
        ttb_time = []
        ttb_iteration = []
        runtime = []

        print(f"\n--- Results for each Run of {instance} ---")
        for i, result in enumerate(runs, 1):
            pprint.pprint(
                f"Run {i}: Solution Value: {result["ObjValue"]} | TtB: (Time: {result["TimeToBest"][2]:.2f} Iteration: {result["TimeToBest"][1]:.0f} | RunTime: {result["Runtime"]:.2f}"
            )
            solution_values.append(result["ObjValue"])
            runtime.append(result["Runtime"])
            ttb_iteration.append(result["TimeToBest"][1])
            ttb_time.append(result["TimeToBest"][2])

        best = min(solution_values)
        avg = np.mean(solution_values)
        std = np.std(solution_values)

        avg_time = np.mean(runtime)
        avg_time_to_best = np.mean(ttb_time)
        avg_iteration_to_best = np.mean(ttb_iteration)
        print(f"\n--- Average Results for {instance} ---")
        print(
            f"\nBest: {best} | Avg: {avg:.2f} | Std: {std:.2f} | Avg_Time: {avg_time:.2f} | Avg_Time_To_Bet: {avg_time_to_best:.2f} | Avg_Time_To_Best_IT: {avg_iteration_to_best:.0f}"
        )
