from enum import Enum
import time


class Interrupt(Enum):
    BY_TIMEOUT = 1
    BY_ITERATION_LIMIT = 2
    BY_TIMEOUT_NO_IMPROVEMENT = 3
    BY_ITERATION_LIMIT_NO_IMPROVEMENT = 4


class StopCondition:
    def __init__(self, method: Interrupt, limit: int):
        self._method = method
        self._limit = limit

        self._starting_time = time.perf_counter()
        self._curr_iteration = 0

        self._methods = {
            Interrupt.BY_TIMEOUT: self._max_time,
            Interrupt.BY_ITERATION_LIMIT: self._max_iteration,
            Interrupt.BY_TIMEOUT_NO_IMPROVEMENT: self._max_time_no_improvement,
            Interrupt.BY_ITERATION_LIMIT_NO_IMPROVEMENT: self._max_iteration_no_improvement,
        }
        self._stop_function = self._methods.get(self._method, lambda: False)

    def stop(self) -> bool:
        return self._stop_function()

    def update_iteration(self) -> None:
        self._curr_iteration += 1

    def _max_time(self) -> bool:
        return time.perf_counter - self._starting_time >= self._limit

    def _max_iteration(self) -> bool:
        return self._curr_iteration >= self._limit

    def _max_time_no_improvement(self) -> bool:
        return False

    def _max_iteration_no_improvement(self) -> bool:
        return False
