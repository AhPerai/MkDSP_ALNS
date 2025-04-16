from typing import Dict
from enum import Enum

import numpy.random as random
from networkx import Graph

from acept_criterion.accept_strategy import AcceptStrategy
from stop.stop_condition import StopCondition
from select.select_strategy import SelectStrategy
from operators.operator_strategy import OperatorStrategy


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

    def add_destroy_operator(self, operator: OperatorStrategy):
        self.__add_operator(OperatorType.DESTROY, operator)

    def add_repair_operator(self, operator: OperatorStrategy):
        self.__add_operator(OperatorType.REPAIR, operator)

    def __add_operator(self, type: OperatorType, operator: OperatorStrategy):
        self._operators[type][operator.name] = operator

    def execute(self, initial_S: Graph) -> Graph:
        best_S = curr_S = initial_S

        while not self._stop.stop():
            destroy_idx, repair_idx = self._select.select()

            d_name, d_operator = list(self._destroy_operators.items())[destroy_idx]
            r_name, r_operator = list(self._repair_operators.items())[repair_idx]

            destroyed_S = d_operator.operate(curr_S)
            new_S = r_operator.operate(destroyed_S)

            best_S, curr_S, outcome = self._accept.evaluate_solution(
                best_S, curr_S, new_S
            )

            self._select.update(destroy_idx, repair_idx, outcome)
            self._accept.update_values()
            self._stop.update_iteration()

        return best_S
