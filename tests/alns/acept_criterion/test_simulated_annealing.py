import numpy.random as random
from algorithms.alns.acept_criterion.simulated_annealing import SimulatedAnnealing


# Test if new solution is always accepted if it's better than the current solution
def test_accepts_better():
    rng = random.default_rng(42)
    sa = SimulatedAnnealing(1, 0.01, 0.95, rng)

    # Como o objetivo é trazer o menor conjunto dominante menor valor é o melhor
    for _ in range(100):
        assert sa._accept(10, 5)
        sa.update_values()


# Test if new solution is always accepted if it's equal to the current solution
def test_accepts_equal():
    rng = random.default_rng(42)
    sa = SimulatedAnnealing(1, 0.01, 0.95, rng)

    for _ in range(100):
        assert sa._accept(curr_S_value=10, new_S_value=10)
        sa.update_values()


# tests if the worse solution is accepted at least sometimes (but not always)
def test_accepts_worse_probabilistically():
    rng = random.default_rng(123)
    sa = SimulatedAnnealing(2, 0.01, 0.95, rng)

    accepted = 0
    trials = 100
    for _ in range(trials):
        if sa._accept(curr_S_value=10, new_S_value=15):
            accepted += 1
    assert 0 < accepted < trials


def test_cooling_rate_acceptance():
    """
    rng = random.default_rng(0)
    The first value draw by this seed it self._rng.uniform(0, 1) == 0.636
    And the second is self._rng.uniform(0, 1) == 0.269
    This way on the:
    1st iteration: p = np.exp(-(11 - 10) / 2) *should be* 0.606
    2st iteration: p = np.exp(-(11 - 10) / 1) *should be* 0.367
    Which means it should not be accepted in the first time, but definitly on the second one
    """

    rng = random.default_rng(0)
    simulated_annealing = SimulatedAnnealing(2, 1, 0.5, rng)
    assert not simulated_annealing._accept(10, 11)
    simulated_annealing.update_values()
    assert simulated_annealing._accept(10, 11)
