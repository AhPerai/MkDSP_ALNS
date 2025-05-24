from typing import List, Dict, Callable

from algorithms.alns.alns import ALNS
from algorithms.alns.stop.stop_condition import StopCondition, Interrupt
from algorithms.alns.select.roulette_wheel import RouletteWheelSelect
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
    ("cooling_rate", float),
    ("segment_lenght", int),
    ("reaction_factor", float),
]


def cast(value, caster: Callable):
    try:
        return caster(value)
    except Exception:
        return value


import pprint


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
            "segment_lenght": 25,
            "reaction_factor": 0.5,
            "outcome_rewards": [33, 0, 16, 0, 9, 0],
        }

    config["repair_operators"] = [
        RandomRepair.name,
        GreedyDegreeOperator.name,
        GreedyLeastDominatedOperator.name,
        GreedyHybridDegreeOperator.name,
        GreedyHybridDominatedOperator.name,
    ]
    config["destroy_operators"] = [RandomDestroy.name]

    return config


def setup_alns(config) -> ALNS:
    rng = np.random.default_rng()
    # repair operators
    random_repair_op = RandomRepair(rng)
    degree_repair_op = GreedyDegreeOperator(config["greedy_alpha"])
    least_dom_repair_op = GreedyLeastDominatedOperator(config["greedy_alpha"])
    hybrid_repair_op_v1 = GreedyHybridDominatedOperator(config["greedy_alpha"])
    hybrid_repair_op_v2 = GreedyHybridDegreeOperator(config["greedy_alpha"])

    # destroy operators
    destroy_op = RandomDestroy(config["destroy_factor"], rng)

    d_op_list = [destroy_op]
    r_op_list = [
        random_repair_op,
        degree_repair_op,
        least_dom_repair_op,
        hybrid_repair_op_v1,
        hybrid_repair_op_v2,
    ]

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

    # select strategy
    seg_roulette_wheel = RouletteWheelSelect(
        num_destroy_op=len(d_op_list),
        num_repair_op=len(r_op_list),
        segment_lenght=config["segment_lenght"],
        reaction_factor=config["reaction_factor"],
        outcome_rewards=config["outcome_rewards"],
        rng=rng,
    )

    # initializing ALNS
    alns = ALNS(
        stop=stop_by_iterations,
        accept=simulated_annealing,
        select=seg_roulette_wheel,
        rng=rng,
        track_stats=True,
    )

    # adding the operators
    for d_operator in d_op_list:
        alns.add_destroy_operator(d_operator)

    for r_operator in r_op_list:
        alns.add_repair_operator(r_operator)

    return alns
