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
    ("greedy_alpha", float, 0.0057),
    ("destroy_factor", float, 0.2666),
    ("method", str, "iteration"),
    ("limit", int, 5000),
    ("initial_temperature", int, 62),
    ("final_temperature", float, 0.1187),
    ("cooling_rate", float, 0.9434),
    ("segment_length", int, 303),
    ("reaction_factor", float, 0.8744),
    ("reward_best", int, 72),
    ("reward_new_better", int, 0),
    ("reward_better", int, 12),
    ("reward_new_accepted", int, 0),
    ("reward_accepted", int, 32),
    ("reward_rejected", int, 0),
]


def get_config_from_args(args):
    config = {}
    reward_list = []
    for key, _, _ in schema:
        if key.startswith("reward_"):
            reward_list.append(getattr(args, key))
        else:
            config[key] = getattr(args, key)

    config["outcome_rewards"] = reward_list
    config["repair_operators"] = [
        RandomRepair.name,
        GreedyDegreeOperator.name,
        GreedyLeastDominatedOperator.name,
        GreedyHybridDegreeOperator.name,
        GreedyHybridDominatedOperator.name,
    ]
    config["destroy_operators"] = [RandomDestroy.name]
    return config


def get_config() -> Dict:

    config = {
        "greedy_alpha": 0.0057,
        "destroy_factor": 0.2666,
        "method": "iteration",
        "limit": 5000,
        "initial_temperature": 62,
        "final_temperature": 0.1187,
        "cooling_rate": 0.9434,
        "segment_length": 303,
        "reaction_factor": 0.8744,
        "outcome_rewards": [72, 0, 12, 0, 32, 0],
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
    degree_repair_op = GreedyDegreeOperator(config["greedy_alpha"], rng)
    least_dom_repair_op = GreedyLeastDominatedOperator(config["greedy_alpha"], rng)
    hybrid_repair_op_v1 = GreedyHybridDominatedOperator(config["greedy_alpha"], rng)
    hybrid_repair_op_v2 = GreedyHybridDegreeOperator(config["greedy_alpha"], rng)

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
        segment_lenght=config["segment_length"],
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
