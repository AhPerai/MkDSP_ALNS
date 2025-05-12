from abc import abstractmethod
from typing import Tuple, List
import numpy as np
from numpy.random import Generator
from algorithms.alns.outcome import Outcome
from algorithms.reset import Resettable


class SelectStrategy(Resettable):

    def __init__(self, num_destroy_op: int, num_repair_op: int, rng: Generator):
        self._num_destroy_op = num_destroy_op
        self._num_repair_op = num_repair_op
        self._destroy_op_weights = np.ones(num_destroy_op)
        self._repair_op_weights = np.ones(num_repair_op)
        self._rng = rng

    @property
    def num_destroy_op(self) -> int:
        return self._num_destroy_op

    @property
    def num_repair_op(self) -> int:
        return self._num_repair_op

    @property
    def destroy_op_weights(self) -> List[float]:
        return self._destroy_op_weights

    @property
    def repair_op_weights(self) -> List[float]:
        return self._repair_op_weights

    @property
    def rng(self) -> Generator:
        return self._rng

    def is_update_time(self) -> bool:
        return False

    @abstractmethod
    def select(self) -> Tuple[int, int]:
        return NotImplemented

    @abstractmethod
    def update(self, destroy_idx: int, repair_idx: int, outcome: Outcome) -> None:
        return NotImplemented

    @abstractmethod
    def reset(self, rng=None):
        return super().reset(rng)
