import pytest
from numpy.testing import assert_, assert_equal, assert_almost_equal
from algorithms.alns.select.roulette_wheel import RouletteWheelSelect
from algorithms.alns.outcome import Outcome
import numpy as np


def test_initial_array_sizes():
    OUTCOME_REWARDS = [2, 0, 1, 0, 1, 0]
    rws = RouletteWheelSelect(3, 2, 5, 0.5, OUTCOME_REWARDS)

    assert rws.destroy_op_weights.shape[0] == 3
    assert rws.repair_op_weights.shape[0] == 2
    assert rws.destroy_scores.shape[0] == 3
    assert rws.repair_scores.shape[0] == 2
    assert rws.destroy_attempts.shape[0] == 3
    assert rws.repair_attempts.shape[0] == 2


@pytest.mark.parametrize(
    "num_d_op, num_r_op, d_op_weights, r_op_weights",
    [
        (2, 2, [1.0, 1.0], [1.0, 1.0]),  # Equal weights
        (3, 3, [2.0, 3.0, 5.0], [4.0, 1.0, 5.0]),  # Unequal weights case
        (4, 4, [0.0, 1.0, 2.0, 1.0], [0.0, 0.5, 1.5, 1.0]),  # Zero weights case
        (1, 1, [10.0], [20.0]),  # Single operator case
    ],
)
def test_roulette_selection_weights_probabilies_sum_equals_one(
    num_d_op, num_r_op, d_op_weights, r_op_weights
):
    OUTCOME_REWARDS = [2, 0, 1, 0, 1, 0]
    rws = RouletteWheelSelect(num_d_op, num_r_op, 5, 0.5, OUTCOME_REWARDS)

    rws._destroy_op_weights = np.array(d_op_weights)
    rws._repair_op_weights = np.array(r_op_weights)

    d_operator_probabilities = rws._destroy_op_weights / np.sum(rws._destroy_op_weights)
    r_operator_probabilities = rws._repair_op_weights / np.sum(rws._repair_op_weights)

    assert_almost_equal(np.sum(d_operator_probabilities), 1.0)
    assert_almost_equal(np.sum(r_operator_probabilities), 1.0)


@pytest.mark.parametrize(
    "seed, expected_r_op_id, expected_d_op_id",
    [
        (3, 0, 0),  # 0.00 <= percent < 0.25
        (2, 1, 1),  # 0.25 <= percent < 0.50
        (23, 2, 2),  # 0.50 <= percent < 0.75
        (5, 3, 3),  # 0.75 <= percent < 1.00
    ],
)
def test_roulette_selection_respects_weights(seed, expected_r_op_id, expected_d_op_id):
    rng = np.random.default_rng(seed)
    OUTCOME_REWARDS = [2, 0, 1, 0, 1, 0]
    rws = RouletteWheelSelect(4, 4, 5, 0.5, OUTCOME_REWARDS, rng)

    rws._destroy_op_weights = np.array([1.0, 1.0, 1.0, 1.0])
    rws._repair_op_weights = np.array([1.0, 1.0, 1.0, 1.0])

    d, r = rws.select()

    assert_equal(d, expected_d_op_id)
    assert_equal(r, expected_r_op_id)


def test_attempt_counters_update():
    OUTCOME_REWARDS = [2, 0, 1, 0, 1, 0]
    rws = RouletteWheelSelect(2, 2, 5, 0.5, OUTCOME_REWARDS)
    rws._destroy_op_weights = np.array([0.5, 0.5])
    rws._repair_op_weights = np.array([0.5, 0.5])

    d, r = rws.select()

    assert rws.destroy_attempts[d] == 1
    assert rws.repair_attempts[r] == 1

    rws._reset_operators()

    d, r = rws.select()

    assert rws.destroy_attempts[d] == 1
    assert rws.repair_attempts[r] == 1


def test_reward_accumulation():
    OUTCOME_REWARDS = [33, 0, 17, 0, 9, 0]
    rws = RouletteWheelSelect(1, 1, 5, 0.5, OUTCOME_REWARDS)

    rws.update(0, 0, Outcome.BEST)
    assert_equal(rws._destroy_scores[0], OUTCOME_REWARDS[Outcome.BEST.id])
    rws._reset_operators()

    outcomes = [Outcome.BEST, Outcome.ACCEPTED, Outcome.BETTER, Outcome.REJECTED]
    for outcome in outcomes:
        rws.update(0, 0, outcome)
    total_reward = sum(OUTCOME_REWARDS[outcome.id] for outcome in outcomes)

    assert_equal(rws._destroy_scores[0], total_reward)


def test_iteration_tracking():
    OUTCOME_REWARDS = [33, 0, 17, 0, 9, 0]
    ITERATION = 10
    rws = RouletteWheelSelect(1, 1, ITERATION, 0.5, OUTCOME_REWARDS)

    for i in range(ITERATION + 1):
        if i == ITERATION:
            assert_equal(rws._iteration, 0)
        else:
            assert_equal(rws._iteration, i)

        rws.update(0, 0, Outcome.BEST)
        rws.select()


def test_reset_after_segment():
    OUTCOME_REWARDS = [33, 0, 17, 0, 9, 0]
    ITERATIONS = 3
    rws = RouletteWheelSelect(1, 1, ITERATIONS, 0.5, OUTCOME_REWARDS)
    rws._destroy_attempts[0] = 2
    rws._repair_attempts[0] = 2
    rws._destroy_scores[0] = 20
    rws._repair_scores[0] = 20

    for _ in range(ITERATIONS):
        rws.update(0, 0, Outcome.BEST)
        rws.select()

    # select resets all attempts to zero, but increases to one by re selecting the operators
    assert_(np.all(rws._destroy_attempts == 1))
    assert_(np.all(rws._repair_attempts == 1))
    # No more updates were called to scores should be zero
    assert_(np.all(rws._destroy_scores == 0))
    assert_(np.all(rws._repair_scores == 0))


def test_weight_update_considers_history():
    OUTCOME_REWARDS = [33, 0, 17, 0, 9, 0]
    rws = RouletteWheelSelect(1, 1, 3, 0.5, OUTCOME_REWARDS)

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


def test_attempt_complete_resets():
    OUTCOME_REWARDS = [33, 0, 17, 0, 9, 0]
    rws = RouletteWheelSelect(2, 2, 11, 0.5, OUTCOME_REWARDS)

    for i in range(10):
        rws.select()

    rws.reset()

    assert_(np.all(rws._destroy_attempts == 0))
    assert_(np.all(rws._repair_attempts == 0))
    assert_(np.all(rws._destroy_scores == 0))
    assert_(np.all(rws._repair_scores == 0))
    assert_(np.all(rws._destroy_op_weights == 1.0))
    assert_(np.all(rws._repair_op_weights == 1.0))
