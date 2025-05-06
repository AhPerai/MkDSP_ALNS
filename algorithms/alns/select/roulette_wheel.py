from algorithms.alns.select.select_strategy import SelectStrategy
from algorithms.alns.outcome import Outcome
from typing import List, Tuple
from numpy.random import Generator
import numpy as np


class RouletteWheelSelect(SelectStrategy):

    def __init__(
        self,
        num_destroy_op: int,
        num_repair_op: int,
        segment_lenght: int,
        reaction_factor: float,
        outcome_rewards: List[int],
        rng: Generator = np.random.default_rng(),
    ):
        super().__init__(num_destroy_op, num_repair_op, rng)
        self._segment_lenght = segment_lenght
        self._reaction_factor = reaction_factor

        # Track current iteration
        self._iteration = 0

        # Track scores and attempts per iteration/segment
        self._destroy_scores = np.zeros(num_destroy_op)
        self._repair_scores = np.zeros(num_repair_op)
        self._destroy_attempts = np.zeros(num_destroy_op)
        self._repair_attempts = np.zeros(num_repair_op)
        self._rewards = outcome_rewards

    @property
    def rewards(self):
        return self._rewards

    @property
    def repair_scores(self):
        return self._repair_scores

    @property
    def repair_scores(self):
        return self._repair_scores

    @property
    def destroy_scores(self):
        return self._destroy_scores

    @property
    def destroy_attempts(self):
        return self._destroy_attempts

    @property
    def repair_attempts(self):
        return self._repair_attempts

    def is_update_time(self):
        return self._iteration == self._segment_lenght

    def _roulette_wheel_selection(self, operators_weigths: List[float]) -> int:
        operators_probabilies = operators_weigths / np.sum(operators_weigths)
        return self._rng.choice(len(operators_weigths), p=operators_probabilies)

    def select(self) -> Tuple[int, int]:
        if self.is_update_time():
            self._reset_operators()

        d_idx = self._roulette_wheel_selection(self._destroy_op_weights)
        r_idx = self._roulette_wheel_selection(self._repair_op_weights)

        self._repair_attempts[r_idx] += 1
        self._destroy_attempts[d_idx] += 1

        return (d_idx, r_idx)

    def update(self, destroy_idx: int, repair_idx: int, outcome: Outcome):
        self._destroy_scores[destroy_idx] += self._rewards[outcome.id]
        self._repair_scores[repair_idx] += self._rewards[outcome.id]

        self._iteration += 1

        if self.is_update_time():
            self._update_weights()

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

    def _reset_operators(self):
        self._destroy_attempts.fill(0)
        self._repair_attempts.fill(0)
        self._destroy_scores.fill(0)
        self._repair_scores.fill(0)
        self._iteration = 0


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    rws = RouletteWheelSelect(4, 4, 5, 0.5, rng)

    rws._destroy_op_weights = np.array([1.0, 1.0, 1.0, 1.0])
    rws._repair_op_weights = np.array([1.0, 1.0, 1.0, 1.0])

    d, r = rws.select()

    print(f"destroy: {d}, repair: {r}")
