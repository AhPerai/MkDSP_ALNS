from typing import Dict, Tuple
from enum import Enum

import numpy.random as random
import copy

from algorithms.solution_state import SolutionState
from algorithms.alns.acept_criterion.accept_strategy import AcceptStrategy
from algorithms.alns.stop.stop_condition import StopCondition
from algorithms.alns.select.select_strategy import SelectStrategy
from algorithms.alns.operators.operator_strategy import OperatorStrategy


class OperatorType(Enum):
    DESTROY = 1
    REPAIR = 2


class ALNS:

    def __init__(
        self,
        stop: StopCondition,
        accept: AcceptStrategy,
        select: SelectStrategy,
        rng: random.Generator = random.default_rng(),
    ):
        self._rng = rng
        self._stop = stop
        self._accept = accept
        self._select = select

        self._destroy_operators: Dict[str, OperatorStrategy] = {}
        self._repair_operators: Dict[str, OperatorStrategy] = {}

        self._operators: Dict[OperatorType, Dict[str, OperatorStrategy]] = {
            OperatorType.DESTROY: self._destroy_operators,
            OperatorType.REPAIR: self._repair_operators,
        }

        self.__destroy_op_list: Tuple[OperatorStrategy]
        self.__repair_op_list: Tuple[OperatorStrategy]

    @property
    def operators(self):
        self._operators

    def add_destroy_operator(self, operator: OperatorStrategy):
        self.__add_operator(OperatorType.DESTROY, operator)

    def add_repair_operator(self, operator: OperatorStrategy):
        self.__add_operator(OperatorType.REPAIR, operator)

    def __add_operator(self, type: OperatorType, operator: OperatorStrategy):
        self._operators[type][operator.name] = operator

    def _init_operators_list(self):
        self.__destroy_op_list = tuple(self._destroy_operators.items())
        self.__repair_op_list = tuple(self._repair_operators.items())

    def setup(self, initial_S: SolutionState):
        self._init_operators_list()

        operators_list = list(self.__destroy_op_list + self.__repair_op_list)
        for op_name, operator in operators_list:
            initial_S.add_info_index(operator.info_indexes)

        initial_S.init_G_info()

        op_name, initial_repair_operator = self.__repair_op_list[1]
        initial_repair_operator.operate(initial_S)
        print(len(initial_S.S))

    def validate(self):
        if (
            len(self._operators[OperatorType.DESTROY]) == 0
            or len(self._operators[OperatorType.REPAIR]) == 0
        ):
            raise ValueError("No repair or destroy operators found")

        # TODO: add validation for a valid solution

    def execute(self, initial_S) -> SolutionState:
        self.validate()
        self.setup(initial_S)

        curr_S = copy.deepcopy(initial_S)
        best_S = copy.deepcopy(initial_S)

        while not self._stop.stop():
            destroy_idx, repair_idx = self._select.select()

            d_name, d_operator = self.__destroy_op_list[destroy_idx]
            r_name, r_operator = self.__repair_op_list[repair_idx]

            destroyed_S = d_operator.operate(copy.deepcopy(curr_S))
            new_S = r_operator.operate(destroyed_S)

            best_S, curr_S, outcome = self._accept.evaluate_solution(
                best_S, curr_S, new_S
            )
            print(f"{self._stop.iteration}: {len(new_S.S)} STATUS: {outcome.label}")

            self._select.update(destroy_idx, repair_idx, outcome)
            self._accept.update_values()

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
from algorithms.alns.operators.repair_operators.greedy_hybrid import (
    GreedyHybridOperator,
)
from algorithms.alns.operators.repair_operators.random_repair import RandomRepair
from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy

if __name__ == "__main__":
    #  fixed variables
    K = 2
    INSTANCE_PATH = "instances/cities_small_instances/bath.txt"
    DESTROY_FACTOR = 0.075
    SEED = 63
    rng = np.random.default_rng(SEED)

    # solution state
    initial_S = SolutionState(INSTANCE_PATH, K)

    # operators
    random_repair_op = RandomRepair(rng)
    degree_repair_op = GreedyDegreeOperator()
    least_dom_repair_op = GreedyLeastDominatedOperator()
    hybrid_repair_op = GreedyHybridOperator()
    destroy_op = RandomDestroy(int(len(initial_S.G) * DESTROY_FACTOR), rng)

    d_op_list = [destroy_op]
    r_op_list = [
        random_repair_op,
        degree_repair_op,
        least_dom_repair_op,
        hybrid_repair_op,
    ]

    # stop condition
    stop_by_iterations = StopCondition(Interrupt.BY_ITERATION_LIMIT, 1000)
    # acceptance criterion
    simulated_annealing = SimulatedAnnealing(7.5, 0.05, 0.95, rng)
    # select strategy
    seg_roulette_wheel = RouletteWheelSelect(
        len(d_op_list), len(r_op_list), 5, 0.5, rng
    )

    # initializing ALNS
    alns = ALNS(
        stop=stop_by_iterations,
        accept=simulated_annealing,
        select=seg_roulette_wheel,
        rng=rng,
    )

    # adding the operators
    for d_operator in d_op_list:
        alns.add_destroy_operator(d_operator)

    for r_operator in r_op_list:
        alns.add_repair_operator(r_operator)

    best_solution = alns.execute(initial_S)
    print(len(best_solution.S))
