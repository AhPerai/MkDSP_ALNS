from enum import Enum
import time
from algorithms.alns.reset import Resettable


class Interrupt(Enum):
    BY_TIMEOUT = 1, "timeout"
    BY_ITERATION_LIMIT = 2, "iteration"
    BY_TIMEOUT_NO_IMPROVEMENT = 3, "timeout_no_improvement"
    BY_ITERATION_LIMIT_NO_IMPROVEMENT = 4, "iteration_no_improvement"

    def __init__(self, id, label):
        self.id = id
        self.label = label

    @classmethod
    def get_by_label(cls, label):
        return cls._label_map[label]


Interrupt._label_map = {member.label: member for member in Interrupt}


class StopCondition(Resettable):
    def __init__(self, method: Interrupt, limit: int):
        if method == None:
            raise ValueError("The stop method condition must be informed")

        if limit <= 0:
            raise ValueError("Limit must be positive")

        self._method = method
        self._limit = limit
        self._starting_time = None
        self._curr_iteration = 0

        self._methods = {
            Interrupt.BY_TIMEOUT: self._max_time,
            Interrupt.BY_ITERATION_LIMIT: self._max_iteration,
            Interrupt.BY_TIMEOUT_NO_IMPROVEMENT: self._max_time_no_improvement,
            Interrupt.BY_ITERATION_LIMIT_NO_IMPROVEMENT: self._max_iteration_no_improvement,
        }
        self._stop_function = self._methods.get(self._method, lambda: False)

    @property
    def iteration(self):
        return self._curr_iteration

    @property
    def starting_time(self):
        return self._starting_time

    @property
    def limit(self):
        return self._limit

    def init_time(self) -> None:
        self._starting_time = time.perf_counter()

    def stop(self) -> bool:
        self.update_iteration()
        return self._stop_function()

    def update_iteration(self) -> None:
        self._curr_iteration += 1

    def _max_time(self) -> bool:
        return time.perf_counter() - self._starting_time >= self._limit

    def _max_iteration(self) -> bool:
        return self._curr_iteration > self._limit

    def _max_time_no_improvement(self) -> bool:
        return False

    def _max_iteration_no_improvement(self) -> bool:
        return False

    def reset(self, rng=None):
        """
        Resets starting_time and iteration for a new execution
        """
        self._starting_time = None
        self._curr_iteration = 0
