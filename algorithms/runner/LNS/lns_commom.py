from typing import List, Dict, Callable

from algorithms.alns.lns import LNS
from algorithms.alns.stop.stop_condition import StopCondition, Interrupt
from algorithms.alns.acept_criterion.simulated_annealing import SimulatedAnnealing

import numpy as np

from algorithms.alns.operators.repair_operators import (
    GreedyDegreeOperator,
    GreedyLeastDominatedOperator,
    GreedyHybridDominatedOperator,
    GreedyHybridDegreeOperator,
    RandomRepair,
)

from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy


schema = [
    ("greedy_alpha", float),
    ("destroy_factor", float),
    ("method", str),
    ("limit", int),
    ("initial_temperature", int),
    ("final_temperature", int),
]


def cast(value, caster: Callable):
    try:
        return caster(value)
    except Exception:
        return value


def get_config(configuration: List = None) -> Dict:
    config = {}
    if configuration:
        for i, (key, caster) in enumerate(schema):
            config[key] = cast(configuration[i], caster)

        config["outcome_rewards"] = list(map(int, configuration[len(schema) :]))
    else:
        config = {
            "greedy_alpha": 0.15,
            "destroy_factor": 0.5,
            "method": "iteration",
            "limit": 10,
            "initial_temperature": 25,
            "final_temperature": 1,
            "cooling_rate": 0.9975,
            "destroy_operator": "random_repair",
            "repair_operator": "random_destroy",
        }

    return config


def setup_alns(config) -> ALNS:
    rng = np.random.default_rng()
    # repair operators
    random_repair_op = RandomRepair(rng)
    degree_repair_op = GreedyDegreeOperator(config["greedy_alpha"])
    # destroy operators
    destroy_op = RandomDestroy(config["destroy_factor"], rng)

    # stop condition
    stop_by_iterations = StopCondition(
        method=Interrupt.get_by_label(config["method"]), limit=config["limit"]
    )

    # acceptance criterion
    simulated_annealing = SimulatedAnnealing(
        initial_temperature=config["initial_temperature"],
        final_temperature=config["final_temperature"],
        cooling_rate=config["cooling_rate"],
        rng=rng,
    )

    # initializing ALNS
    alns = LNS(
        stop=stop_by_iterations,
        accept=simulated_annealing,
        rng=rng,
        track_stats=True,
    )

    # adding the operators
    for d_operator in d_op_list:
        alns.add_destroy_operator(d_operator)

    for r_operator in r_op_list:
        alns.add_repair_operator(r_operator)

    return alns
