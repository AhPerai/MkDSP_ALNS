from typing import Dict, Tuple
from enum import Enum

import numpy as np
import random
import copy

from algorithms.solution_state import SolutionState
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

    def randomize_rng(self):
        seed = random.randint(0, 2**32 - 1)
        self._rng = np.random.default_rng(seed)

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

        op_name, initial_repair_operator = self._repair_op_list[1]
        initial_repair_operator.operate(initial_S)

        for d_name, d_operator in self._destroy_op_list:
            d_operator.remove_value = int(len(initial_S.S) * 0.5)

        if self._track_stats:
            self._stats = Statistics(self)
            self.stats.add_data_trackers()

    def validate(self):
        if self.n_destroy_operators == 0 or self.n_repair_operators == 0:
            raise ValueError("No repair or destroy operators found")

    def execute(self, initial_S) -> SolutionState:
        self.validate()
        self.setup(initial_S)

        curr_S = initial_S.copy()
        best_S = initial_S.copy()

        while not self._stop.stop():
            print(self.stop.iteration)
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

            self._events.on_outcome(outcome, new_S)

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

import os

if __name__ == "__main__":
    #  fixed variables
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/glasgow.txt"
    SEED = 51237823156
    GREEDY_ALPHA = 0.1
    rng = np.random.default_rng(SEED)

    # operators

    # repair
    random_repair_op = RandomRepair(rng)
    degree_repair_op = GreedyDegreeOperator(GREEDY_ALPHA)
    least_dom_repair_op = GreedyLeastDominatedOperator(GREEDY_ALPHA)
    hybrid_repair_op_v1 = GreedyHybridDominatedOperator(GREEDY_ALPHA)
    hybrid_repair_op_v2 = GreedyHybridDegreeOperator(GREEDY_ALPHA)
    # destroy
    destroy_op = RandomDestroy(rng)

    d_op_list = [destroy_op]
    r_op_list = [
        random_repair_op,
        degree_repair_op,
        least_dom_repair_op,
        hybrid_repair_op_v1,
        hybrid_repair_op_v2,
    ]

    # stop condition
    stop_by_iterations = StopCondition(Interrupt.BY_ITERATION_LIMIT, 2000)
    # acceptance criterion
    simulated_annealing = SimulatedAnnealing(5, 0.5, 0.995, rng)
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

    results = []
    # for _ in range(10):
    # alns.randomize_rng()

    initial_S = SolutionState(INSTANCE_PATH, K)
    best_solution = alns.execute(initial_S)
    results.append(len(best_solution.S))

    best = min(results)
    avg = np.mean(results)
    std = np.std(results)

    import pprint

    print(f"0. runtime duration: {alns.stats.get_runtime_duration()}")
    # pprint.pprint(alns.stats.best_solution_tracking)
    print("1. repair weight progression")
    for op in range(len(alns.stats.repair_operators_weights)):
        weights = alns.stats.repair_operators_weights[op]
        formatted_weights = [f"{w:.2f}" for w in weights]
        print(f"{alns._repair_op_list[op][0]}:\n {formatted_weights}\n")

    # pprint.pprint(alns.stats.repair_operators_weights)
    print("2. destroy weight progression")
    for op in range(len(alns.stats.destroy_operators_weights)):
        weights = alns.stats.destroy_operators_weights[op]
        formatted_weights = [f"{w:.2f}" for w in weights]
        print(f"{alns._destroy_op_list[op][0]}:\n {formatted_weights}\n")

    print("3. Tracking Best Solution\n")
    pprint.pprint(alns.stats.best_solution_tracking)

    print("\n4. Last Best Solution")
    print(alns.stats.get_last_time_to_best())
    print(f"Instance: {INSTANCE_PATH} | Best: {best} | Avg: {avg:.2f} | Std: {std:.2f}")
