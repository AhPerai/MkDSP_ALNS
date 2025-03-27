from abc import ABC, abstractmethod
from typing import Tuple
from networkx import Graph


class SelectStrategy(ABC):

    def __init__(self, num_destroy_op: int, num_repair_op: int):
        self._num_destroy_op = num_destroy_op
        self._num_repair_op = num_repair_op

    @property
    def num_destroy_op(self) -> int:
        return self._num_destroy_op

    @property
    def num_repair_op(self) -> int:
        return self._num_destroy_op

    @abstractmethod
    def select(self) -> Tuple[int, int]:
        return NotImplemented

    @abstractmethod
    def update(self, destroy_idx: int, repair_idx: int, accepted: bool) -> None:
        return NotImplemented
