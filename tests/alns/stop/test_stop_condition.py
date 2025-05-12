import pytest
from numpy.testing import assert_, assert_equal
from algorithms.alns.stop.stop_condition import StopCondition, Interrupt


"""
Max Iterations Test
"""
ITERATION = 100


def test_dont_stop_before_max_iterations():
    condition = StopCondition(Interrupt.BY_ITERATION_LIMIT, ITERATION)

    for _ in range(ITERATION):
        assert_(not condition.stop())


def test_reached_iteration_limit_on_stop():
    condition = StopCondition(Interrupt.BY_ITERATION_LIMIT, ITERATION)

    iteration_counter = 0
    for _ in range(ITERATION):
        iteration_counter += 1
        condition.stop()

    assert_equal(iteration_counter, condition.iteration)


def test_stop_after_max_iterations():
    condition = StopCondition(Interrupt.BY_ITERATION_LIMIT, ITERATION)

    for _ in range(ITERATION):
        condition.stop()

    for _ in range(ITERATION):
        assert_(condition.stop())


"""
Time Limit Test
"""

import time


@pytest.mark.parametrize("time_limit", [1, 0.10, 0.05])
def test_dont_stop_before_time_limit(time_limit):
    condition = StopCondition(Interrupt.BY_TIMEOUT, time_limit)
    condition.init_time()

    for _ in range(100):
        assert_(not condition.stop())


def test_stop_after_time_limit():
    condition = StopCondition(Interrupt.BY_TIMEOUT, 1)
    condition.init_time()
    time.sleep(1.05)

    for _ in range(100):
        assert_(condition.stop())


def test_stop_values_after_reset():
    condition = StopCondition(Interrupt.BY_ITERATION_LIMIT, ITERATION)
    condition.init_time()

    for _ in range(ITERATION):
        assert not condition.stop()

    for _ in range(ITERATION):
        assert_(condition.stop())

    condition.reset()
    assert_(condition._starting_time == None)
    assert_(condition._curr_iteration == 0)
    condition.init_time()

    for _ in range(ITERATION):
        assert not condition.stop()
