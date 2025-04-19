from algorithms.alns.acept_criterion.accept_strategy import AcceptStrategy
from numpy.random import Generator
import numpy as np
import numpy.random as random


class SimulatedAnnealing(AcceptStrategy):

    def __init__(
        self,
        initial_temperature,
        final_temperature,
        cooling_rate,
        rng: Generator = np.random.default_rng(),
    ):
        if any(t < 0 for t in [initial_temperature, final_temperature, cooling_rate]):
            raise ValueError("Temperaturas abaixo de 0")

        if initial_temperature < final_temperature:
            raise ValueError("Temperatura inicial deve ser superior a final")

        if cooling_rate > 1:
            raise ValueError("Grau de resfiramento não pode ser superior a 1")

        self._rng = rng
        self._cooling_rate = cooling_rate
        self._initial_temperature = initial_temperature
        self._temperature = initial_temperature
        self._final_temperature = final_temperature

    @property
    def rng(self):
        return self._rng

    @property
    def cooling_rate(self):
        return self._cooling_rate

    @property
    def initial_temperature(self):
        return self._initial_temperature

    @property
    def final_temperature(self):
        return self._final_temperature

    @property
    def current_temperature(self):
        return self._temperature

    def _accept(self, curr_S_value: int, new_S_value: int) -> bool:
        p = np.exp(-(new_S_value - curr_S_value) / self._temperature)
        return self._rng.uniform(0, 1) < p

    def update_values(self) -> None:
        self._temperature = max(
            (self._temperature * self._cooling_rate), self._final_temperature
        )
