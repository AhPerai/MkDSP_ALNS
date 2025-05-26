from typing import Dict, Tuple

import numpy as np

from algorithms.alns.enum.alns_enum import OperatorType
from algorithms.solution_state import SolutionState, Index
from algorithms.alns.acept_criterion.accept_strategy import AcceptStrategy
from algorithms.alns.stop.stop_condition import StopCondition
from algorithms.alns.select.select_strategy import SelectStrategy
from algorithms.alns.operators.operator_strategy import OperatorStrategy

from algorithms.alns.event_handler import Event, EventHandler
from algorithms.alns.statistics import Statistics
from algorithms.alns.reset import Resettable

from algorithms.alns.operators.repair_operators.random_repair import RandomRepair


class ALNS(Resettable):

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
    def select(self) -> SelectStrategy:
        return self._select

    @property
    def rng(self) -> np.random.Generator:
        return self._rng

    @property
    def operators(self) -> Dict[OperatorType, Dict[str, OperatorStrategy]]:
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

        for op_name, operator in list(self._destroy_op_list + self._repair_op_list):
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
            self._accept.update_values()

        self._events.trigger(Event.ON_END)
        return best_S

    def restart_components(self):
        """
        Resets all the components of ALNS once all the operators weights' hit 0
        hopefully searching in new neighboorhoods
        """
        pass

    def reset(self, rng=np.random.default_rng()):
        """
        Resets all the components of ALNS to have a fresh start at a new execution
        """
        self._rng = rng
        self.stop.reset()
        self.select.reset(rng)
        self.accept.reset(rng)
        self.events.unregister_all()
        self._stats = None  # making sure cyclical reference doesnt hold on to memory

        for operator in self.operators[OperatorType.DESTROY].values():
            operator.reset(rng)

        for operator in self.operators[OperatorType.REPAIR].values():
            operator.reset(rng)

    def clear(self):
        """
        Clears all the components to avoid memory leaks
        """
        self._stop = None
        self._select = None
        self._accept = None
        self._events.unregister_all()
        self._events = None
        self._stats = None
