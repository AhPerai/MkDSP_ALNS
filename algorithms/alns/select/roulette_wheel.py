from select.select_strategy import SelectStrategy
from alns.outcome import Outcome
from typing import List, Tuple
import numpy as np
from numpy import Generator


class RouletteWheelSelect(SelectStrategy):

    def __init__(
        self,
        num_destroy_op: int,
        num_repair_op: int,
        rng: Generator,
        segment_lenght: int,
        reaction_factor: int,
    ):
        super.__init__(self, num_destroy_op, num_repair_op, rng)
        self._segment_lenght = segment_lenght
        self._reaction_factor = reaction_factor

        # Track current iteration
        self._iteration = 0

        # Track scores and attempts per iteration
        self._destroy_scores = np.zeros(num_destroy_op)
        self._repair_scores = np.zeros(num_repair_op)
        self._destroy_attempts = np.zeros(num_destroy_op)
        self._repair_attempts = np.zeros(num_repair_op)

    def _roulette_wheel_selection(self, operators_weigths: List[float]) -> int:
        # normalizes the weights
        operators_probabilies = operators_weigths / np.sum(operators_weigths)
        return self._rng.choice(range(len(operators_weigths)), p=operators_probabilies)

    def select(self) -> Tuple[int, int]:
        d_idx = self._roulette_wheel_selection(self._destroy_op_weights)
        r_idx = self._roulette_wheel_selection(self._repair_op_weights)

        # Update Attempts
        self._repair_attempts[r_idx] += 1
        self._destroy_attempts[d_idx] += 1

        return (d_idx, r_idx)

    def update(self, destroy_idx: int, repair_idx: int, outcome: Outcome):
        self._destroy_scores[destroy_idx] += outcome.reward
        self._repair_scores[repair_idx] += outcome.reward

        self._iteration += 1

        if self._iteration == self._segment_lenght:
            self._update_weights()
            self._reset()

    def _update_weights(self):
        for i in range(self._num_destroy_op):
            if self._destroy_attempts[i] > 0:
                avg_score = self._destroy_scores[i] / self._destroy_attempts[i]
                self._destroy_op_weights[i] = (
                    self._destroy_op_weights[i] * (1 - self._reaction_factor)
                    + self._reaction_factor * avg_score
                )

        for i in range(self._num_repair_op):
            if self._repair_attempts[i] > 0:
                avg_score = self._repair_scores[i] / self._repair_attempts[i]
                self._repair_op_weights[i] = (
                    self._repair_op_weights[i] * (1 - self._reaction_factor)
                    + self._reaction_factor * avg_score
                )

    def _reset(self):
        self._destroy_attempts.fill(0)
        self._repair_attempts.fill(0)
        self._destroy_scores.fill(0)
        self._repair_scores.fill(0)
