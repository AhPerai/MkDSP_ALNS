from __future__ import annotations
from algorithms.alns.event_handler import Event
from typing import List, Tuple, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from algorithms.alns.ALNS import ALNS


class Statistics:

    def __init__(self, alns: ALNS):
        self.__alns = alns
        self.num_destroy_op = self.__alns.n_destroy_operators
        self.num_repair_op = self.__alns.n_repair_operators
        self.initialize_properties()

        if self.num_destroy_op == 1 and self.num_repair_op == 1:
            return

        self.initialize_operators_metrics()

    def initialize_properties(self):
        self.__start_time = self.__alns.stop.starting_time
        self.__end_time = None

        self.best_solution_tracking: List[Tuple[int, int, float, str]] = [
            (0, 0, self.__start_time - self.__start_time, "None")
        ]

    def initialize_operators_metrics(self):
        self.destroy_operators_calls = [[] for _ in range(self.num_destroy_op)]
        self.destroy_operators_scores = [[] for _ in range(self.num_destroy_op)]
        self.destroy_operators_weights = [[1.0] for _ in range(self.num_destroy_op)]

        self.repair_operators_calls = [[] for _ in range(self.num_repair_op)]
        self.repair_operators_scores = [[] for _ in range(self.num_repair_op)]
        self.repair_operators_weights = [[1.0] for _ in range(self.num_repair_op)]

    def get_runtime_duration(self):
        return self.__end_time - self.__start_time

    def get_last_time_to_best(self):
        return self.best_solution_tracking[-1]

    def add_basic_data_tracker(self):
        self.track_finishing_time()
        self.track_time_to_best()

    def add_ALNS_data_trackers(self):
        self.add_basic_data_tracker()
        self.track_operators_performance()

    def track_finishing_time(self):
        self.__alns.events.register(Event.ON_END, self.register_end_time)

    def track_time_to_best(self):
        self.__alns.events.register(Event.ON_BEST, self.get_iteration_and_time_on_best)

    def track_operators_performance(self):
        self.__alns.events.register(
            Event.ON_SELECT_UPDATE, self.update_operator_data_from_segment
        )

    def register_end_time(self):
        self.__end_time = time.perf_counter()

    def get_iteration_and_time_on_best(self, new_best_solution, operator_name):
        diff_time = time.perf_counter() - self.__start_time
        self.best_solution_tracking.append(
            (
                len(new_best_solution.S),
                self.__alns.stop.iteration,
                diff_time,
                operator_name,
            )
        )

    def update_operator_data_from_segment(self, destroy_idx, repair_idx, outcome):
        if self.__alns.select.is_update_time():
            for idx_op in range(self.num_repair_op):
                self.repair_operators_calls[idx_op].append(
                    self.__alns.select.repair_attempts[idx_op]
                )
                self.repair_operators_scores[idx_op].append(
                    self.__alns.select.repair_scores[idx_op]
                )
                self.repair_operators_weights[idx_op].append(
                    self.__alns.select.repair_op_weights[idx_op]
                )

            for idx_op in range(self.num_destroy_op):
                self.destroy_operators_calls[idx_op].append(
                    self.__alns.select.destroy_attempts[idx_op]
                )
                self.destroy_operators_scores[idx_op].append(
                    self.__alns.select.destroy_scores[idx_op]
                )
                self.destroy_operators_weights[idx_op].append(
                    self.__alns.select.destroy_op_weights[idx_op]
                )
