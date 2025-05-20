from __future__ import annotations
from algorithms.alns.event_handler import Event
from algorithms.alns.enum.alns_enum import OperatorType
from typing import List, Tuple, Dict, TYPE_CHECKING
import time
import pprint

if TYPE_CHECKING:
    from algorithms.alns.alns import ALNS
    from algorithms.alns.lns import LNS


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
        self.track_finishing_time()
        self.track_time_to_best()
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
                    int(self.__alns.select.repair_attempts[idx_op])
                )
                self.repair_operators_scores[idx_op].append(
                    float(self.__alns.select.repair_scores[idx_op])
                )
                self.repair_operators_weights[idx_op].append(
                    float(self.__alns.select.repair_op_weights[idx_op])
                )

            for idx_op in range(self.num_destroy_op):
                self.destroy_operators_calls[idx_op].append(
                    int(self.__alns.select.destroy_attempts[idx_op])
                )
                self.destroy_operators_scores[idx_op].append(
                    float(self.__alns.select.destroy_scores[idx_op])
                )
                self.destroy_operators_weights[idx_op].append(
                    float(self.__alns.select.destroy_op_weights[idx_op])
                )

    def get_metrics(self) -> Dict:
        if self.__alns.__class__.__name__ == "ALNS":
            return self.get_alns_metrics()

        if self.__alns.__class__.__name__ == "LNS":
            self.get_alns_metrics()

    def get_alns_metrics(self) -> Dict:
        r_op_matrix = {
            operator_name: []
            for operator_name in self.__alns.operators[OperatorType.REPAIR]
        }
        d_op_matrix = {
            operator_name: []
            for operator_name in self.__alns.operators[OperatorType.DESTROY]
        }

        for idx_d_op, op_name in enumerate(self.__alns.operators[OperatorType.DESTROY]):
            d_op_matrix[op_name].append(
                {
                    "attempt": self.destroy_operators_calls[idx_d_op],
                    "score": self.destroy_operators_scores[idx_d_op],
                    "weight": self.destroy_operators_weights[idx_d_op],
                }
            )

        for idx_r_op, op_name in enumerate(self.__alns.operators[OperatorType.REPAIR]):
            r_op_matrix[op_name].append(
                {
                    "attempt": self.repair_operators_calls[idx_r_op],
                    "score": self.repair_operators_scores[idx_r_op],
                    "weight": self.repair_operators_weights[idx_r_op],
                }
            )

        metrics = {
            "best_solution_progression": self.best_solution_tracking,
            "d_op_progression": d_op_matrix,
            "r_op_progression": r_op_matrix,
        }
        return metrics

    def get_lns_metrics(self) -> Dict:
        metrics = {
            "best_solution_progression": self.best_solution_tracking,
        }

        return metrics
