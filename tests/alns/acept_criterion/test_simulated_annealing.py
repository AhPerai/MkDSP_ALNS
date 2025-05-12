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
        sa.update_values()
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


def test_sa_reset_temperature():
    rng = random.default_rng(42)
    sa = SimulatedAnnealing(
        initial_temperature=10, cooling_rate=0.9, final_temperature=1, rng=rng
    )

    for i in range(10):
        sa.update_values()
    sa.reset()

    assert (
        sa.current_temperature == sa.initial_temperature
    ), f"Expected temperature {sa.initial_temperature}, got {sa.current_temperature}"


def test_sa_reset_acceptance_behavior_after_reset():
    """
    Setup: rng seeded with 0 → first uniform draws are predictable.
    1st uniform: 0.636
    2nd uniform: 0.269

    With initial_temperature=2:
    - first p = exp(-(11-10)/2) ≈ 0.606 → should NOT accept (0.636 > 0.606)
    - after update (temperature drops to 1), p = exp(-(11-10)/1) ≈ 0.367 → should accept (0.269 < 0.367)
    """
    rng = random.default_rng(1)
    sa = SimulatedAnnealing(
        initial_temperature=2, final_temperature=1, cooling_rate=0.5, rng=rng
    )

    # Should accept
    assert sa._accept(10, 11)

    # Update → lowers temperature
    sa.update_values()

    # Should NOT accept after update
    accepted_second = sa._accept(10, 11)
    assert not accepted_second, "Expected second acceptance to be True"

    # Upon reseting the same behavior is expected beucase the temperature is back to its initial value
    sa.reset(rng)
    assert sa._accept(10, 11)
