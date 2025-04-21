import pytest
from numpy.testing import assert_, assert_equal, assert_almost_equal
from algorithms.alns.select.roulette_wheel import RouletteWheelSelect
from algorithms.alns.outcome import Outcome
import numpy as np


def test_initial_array_sizes():
    rws = RouletteWheelSelect(3, 2, 5, 0.5)

    assert rws.destroy_op_weights.shape[0] == 3
    assert rws.repair_op_weights.shape[0] == 2
    assert rws.destroy_scores.shape[0] == 3
    assert rws.repair_scores.shape[0] == 2
    assert rws.destroy_attempts.shape[0] == 3
    assert rws.repair_attempts.shape[0] == 2


def test_attempt_counters_update():
    rws = RouletteWheelSelect(2, 2, 5, 0.5)
    rws._destroy_op_weights = np.array([0.5, 0.5])
    rws._repair_op_weights = np.array([0.5, 0.5])

    d, r = rws.select()

    assert rws.destroy_attempts[d] == 1
    assert rws.repair_attempts[r] == 1

    rws._reset()

    d, r = rws.select()

    assert rws.destroy_attempts[d] == 1
    assert rws.repair_attempts[r] == 1


def test_reward_accumulation():
    rws = RouletteWheelSelect(1, 1, 5, 0.5)

    rws.update(0, 0, Outcome.BEST)
    assert_equal(rws._destroy_scores[0], Outcome.BEST.reward)
    rws._reset()

    outcomes = [Outcome.BEST, Outcome.ACCEPTED, Outcome.BETTER, Outcome.REJECTED]
    for outcome in outcomes:
        rws.update(0, 0, outcome)
    total_reward = sum(outcome.reward for outcome in outcomes)

    assert_equal(rws._destroy_scores[0], total_reward)


def test_iteration_tracking():
    ITERATION = 10
    rws = RouletteWheelSelect(1, 1, ITERATION, 0.5)

    for i in range(ITERATION + 1):
        if i == ITERATION:
            assert_equal(rws._iteration, 0)
        else:
            assert_equal(rws._iteration, i)

        rws.update(0, 0, Outcome.BEST)


def test_reset_after_segment():
    rws = RouletteWheelSelect(1, 1, 3, 0.5)
    rws._destroy_attempts[0] = 2
    rws._repair_attempts[0] = 2
    rws._destroy_scores[0] = 20
    rws._repair_scores[0] = 20

    for _ in range(3):
        rws.update(0, 0, Outcome.BEST)

    assert_(np.all(rws._destroy_attempts == 0))
    assert_(np.all(rws._repair_attempts == 0))
    assert_(np.all(rws._destroy_scores == 0))
    assert_(np.all(rws._repair_scores == 0))


def test_weight_update_considers_history():
    rws = RouletteWheelSelect(1, 1, 3, 0.5)

    # manually set some initial weight
    rws._destroy_op_weights[0] = 10
    rws._repair_op_weights[0] = 10

    # simulate attempts and scores
    rws._destroy_scores[0] = 4
    rws._destroy_attempts[0] = 2  # avg = 2
    rws._repair_scores[0] = 2
    rws._repair_attempts[0] = 1  # avg = 2

    rws._update_weights()

    # final weight = 0.5 * old + 0.5 * avg = (10 + 2) / 2 = 6
    assert_almost_equal(rws._destroy_op_weights[0], 6.0)
    assert_almost_equal(rws._repair_op_weights[0], 6.0)
