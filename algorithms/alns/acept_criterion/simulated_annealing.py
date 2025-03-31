from accept_strategy import AcceptStrategy
from networkx import Graph
from numpy.random import Generator
import numpy as np


class SimulatedAnnealing(AcceptStrategy):

    def __init__(self, rng: Generator, initial_temperature, cooling_rate):
        self._rng = rng
        self._cooling_rate = cooling_rate
        self._initial_temperature = initial_temperature
        self._temperature = initial_temperature

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
    def current_temperature(self):
        return self._temperature

    def _accept(self, curr_S: Graph, new_S: Graph) -> bool:
        p = np.exp(-(len(curr_S) - len(new_S)) / self._temperature)
        return self._rng.uniform(0, 1) < p

    def update_values(self) -> None:
        self._temperature *= self._cooling_rate
