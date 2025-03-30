from abc import ABC, abstractmethod
from typing import Tuple
from numpy import Generator


class SelectStrategy(ABC):

    def __init__(self, num_destroy_op: int, num_repair_op: int, rng: Generator):
        self._num_destroy_op = num_destroy_op
        self._num_repair_op = num_repair_op
        self._destroy_op_weights = self._num_destroy_op * [1.0]
        self._repair_op_weights = self._num_repair_op * [1.0]
        self._rng = rng

    @property
    def destroy_op_weights(self) -> int:
        return self._destroy_op_weights

    @property
    def repair_op_weights(self) -> int:
        return self._repair_op_weights

    @property
    def rng(self) -> Generator:
        return self._rng

    @abstractmethod
    def select(self) -> Tuple[int, int]:
        return NotImplemented

    @abstractmethod
    def update(self, destroy_idx: int, repair_idx: int) -> None:
        return NotImplemented
