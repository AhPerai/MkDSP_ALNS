from enum import Enum


class Interrupt(Enum):
    BY_TIMEOUT = 1
    BY_ITERATION_LIMIT = 2
    BY_TIMEOUT_NO_IMPROVEMENT = 3
    BY_ITERATION_LIMIT_NO_IMPROVEMENT = 4


class StopCondition:
    def __init__(self, method: Interrupt, limit: int):
        self._method = method
        self._limit = limit
        self._methods = {
            Interrupt.BY_TIMEOUT: self._max_time,
            Interrupt.BY_ITERATION_LIMIT: self._max_iteration,
            Interrupt.BY_TIMEOUT_NO_IMPROVEMENT: self._max_time_no_improvement,
            Interrupt.BY_ITERATION_LIMIT_NO_IMPROVEMENT: self._max_iteration_no_improvement,
        }
        self._stop_function = self._methods.get(self._method, lambda: False)

    def stop(self) -> bool:
        return self._stop_function()

    def _max_time(self) -> bool:
        pass

    def _max_iteration(self) -> bool:
        pass

    def _max_time_no_improvement(self) -> bool:
        return False

    def _max_iteration_no_improvement(self) -> bool:
        return False
