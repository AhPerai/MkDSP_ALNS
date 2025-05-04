from typing import Dict, Tuple
from enum import Enum

import numpy as np
import random

from algorithms.solution_state import SolutionState, Index
from algorithms.alns.acept_criterion.accept_strategy import AcceptStrategy
from algorithms.alns.stop.stop_condition import StopCondition
from algorithms.alns.select.select_strategy import SelectStrategy
from algorithms.alns.operators.operator_strategy import OperatorStrategy

from algorithms.alns.event_handler import Event, EventHandler
from algorithms.alns.statistics import Statistics


class OperatorType(Enum):
    DESTROY = 1
    REPAIR = 2


class ALNS:

    def __init__(
        self,
        stop: StopCondition,
        accept: AcceptStrategy,
        select: SelectStrategy,
        events: EventHandler = EventHandler(),
        rng: np.random.Generator = np.random.default_rng(),
        track_stats: bool = False,
    ):
        self._rng = rng
        self._stop = stop
        self._accept = accept
        self._select = select
        self._events = events
        self._stats = None
        self._track_stats = track_stats

        self._destroy_operators: Dict[str, OperatorStrategy] = {}
        self._repair_operators: Dict[str, OperatorStrategy] = {}

        self._operators: Dict[OperatorType, Dict[str, OperatorStrategy]] = {
            OperatorType.DESTROY: self._destroy_operators,
            OperatorType.REPAIR: self._repair_operators,
        }

        self._destroy_op_list: Tuple[OperatorStrategy]
        self._repair_op_list: Tuple[OperatorStrategy]

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
    def select(self):
        return self._select

    @property
    def operators(self):
        return self._operators

    @property
    def n_repair_operators(self):
        return len(self._operators[OperatorType.REPAIR])

    @property
    def n_destroy_operators(self):
        return len(self._operators[OperatorType.DESTROY])

    def add_destroy_operator(self, operator: OperatorStrategy):
        self.__add_operator(OperatorType.DESTROY, operator)

    def add_repair_operator(self, operator: OperatorStrategy):
        self.__add_operator(OperatorType.REPAIR, operator)

    def __add_operator(self, type: OperatorType, operator: OperatorStrategy):
        self._operators[type][operator.name] = operator

    def _init_operators_list(self):
        self._destroy_op_list = tuple(self._destroy_operators.items())
        self._repair_op_list = tuple(self._repair_operators.items())

    def setup(self, initial_S: SolutionState):
        self._stop.init_time()
        self._init_operators_list()

        operators_list = list(self._destroy_op_list + self._repair_op_list)
        for op_name, operator in operators_list:
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
            self.stats.add_ALNS_data_trackers()

    def validate(self):
        if self.n_destroy_operators == 0 or self.n_repair_operators == 0:
            raise ValueError("No repair or destroy operators found")

    def execute(self, initial_S) -> SolutionState:
        self.validate()
        self.setup(initial_S)

        curr_S = initial_S.copy()
        best_S = initial_S.copy()

        while not self._stop.stop():
            # print(self.stop.iteration)
            destroy_idx, repair_idx = self._select.select()

            d_name, d_operator = self._destroy_op_list[destroy_idx]
            r_name, r_operator = self._repair_op_list[repair_idx]

            self._events.trigger(
                Event.ON_SELECT, (d_name, d_operator), (r_name, r_operator)
            )

            destroyed_S = d_operator.operate(curr_S.copy())
            new_S = r_operator.operate(destroyed_S)

            best_S, curr_S, outcome = self._accept.evaluate_solution(
                best_S, curr_S, new_S
            )

            self._events.on_outcome(outcome, new_S, r_name)

            self._select.update(destroy_idx, repair_idx, outcome)
            self._events.trigger(
                Event.ON_SELECT_UPDATE, destroy_idx, repair_idx, outcome
            )

        self._events.trigger(Event.ON_END)
        return best_S


# For test purposes
from algorithms.alns.stop.stop_condition import Interrupt
from algorithms.alns.select.roulette_wheel import RouletteWheelSelect
from algorithms.alns.acept_criterion.simulated_annealing import SimulatedAnnealing
import numpy as np


from algorithms.alns.operators.repair_operators.greedy_degree import (
    GreedyDegreeOperator,
)
from algorithms.alns.operators.repair_operators.greedy_least_dom import (
    GreedyLeastDominatedOperator,
)
from algorithms.alns.operators.repair_operators.greedy_hybrid_dom import (
    GreedyHybridDominatedOperator,
)
from algorithms.alns.operators.repair_operators.greedy_hybrid_degree import (
    GreedyHybridDegreeOperator,
)
from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy


def run_ALNS(K, path):
    #  fixed variables
    GREEDY_ALPHA = 0.1
    DESTROY_FACTOR = 0.5
    ITERATION = 10
    rng = np.random.default_rng()

    # operators
    # repair
    random_repair_op = RandomRepair(rng)
    degree_repair_op = GreedyDegreeOperator(GREEDY_ALPHA)
    least_dom_repair_op = GreedyLeastDominatedOperator(GREEDY_ALPHA)
    hybrid_repair_op_v1 = GreedyHybridDominatedOperator(GREEDY_ALPHA)
    hybrid_repair_op_v2 = GreedyHybridDegreeOperator(GREEDY_ALPHA)
    # destroy
    destroy_op = RandomDestroy(DESTROY_FACTOR, rng)

    d_op_list = [destroy_op]
    r_op_list = [
        random_repair_op,
        degree_repair_op,
        least_dom_repair_op,
        hybrid_repair_op_v1,
        hybrid_repair_op_v2,
    ]

    # stop condition
    stop_by_iterations = StopCondition(Interrupt.BY_ITERATION_LIMIT, ITERATION)
    # acceptance criterion
    simulated_annealing = SimulatedAnnealing(10, 1, 0.99, rng)
    # select strategy
    seg_roulette_wheel = RouletteWheelSelect(
        len(d_op_list), len(r_op_list), 50, 0.5, rng
    )

    # initializing ALNS
    alns = ALNS(
        stop=stop_by_iterations,
        accept=simulated_annealing,
        select=seg_roulette_wheel,
        rng=rng,
        track_stats=True,
    )

    # adding the operators
    for d_operator in d_op_list:
        alns.add_destroy_operator(d_operator)

    for r_operator in r_op_list:
        alns.add_repair_operator(r_operator)

    initial_S = SolutionState(path, K)
    best_solution = alns.execute(initial_S)
    return {
        "ObjValue": len(best_solution.S),
        "TimeToBest": alns.stats.get_last_time_to_best(),
        "Runtime": alns.stats.get_runtime_duration(),
    }


if __name__ == "__main__":
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/leeds.txt"

    results = []
    for _ in range(5):
        stats = run_ALNS(K, INSTANCE_PATH)
        results.append(stats)

    print("\n === RESULTS ===")
    solution_sizes = [res["ObjValue"] for res in results]
    ttb_time = [res["TimeToBest"][2] for res in results]
    ttb_iteration = [res["TimeToBest"][1] for res in results]
    runtime = [res["Runtime"] for res in results]

    import pprint

    for result in results:
        pprint.pprint(
            f"Solution Value: {result["ObjValue"]} | TtB: (Time: {result["TimeToBest"][2]:.2f} Iteration: {result["TimeToBest"][1]:.0f} | RunTime: {result["Runtime"]:.2f}"
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
