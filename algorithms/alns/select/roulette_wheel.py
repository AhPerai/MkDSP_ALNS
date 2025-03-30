from select.select_strategy import SelectStrategy
from typing import List, Tuple
import numpy as np


class RouletteWheelSelect(SelectStrategy):

    def _roulette_wheel_selection(self, operators_weigths: List[float]) -> int:
        # normalizes the weights
        operators_probabilies = operators_weigths / np.sum(operators_weigths)
        return self._rng.choice(operators_weigths, p=operators_probabilies)

    def select(self) -> Tuple[int, int]:
        d_idx = self._roulette_wheel_selection(self._destroy_op_weights)
        r_idx = self._roulette_wheel_selection(self._repair_op_weights)
        return (d_idx, r_idx)

    def update(self):
        pass
