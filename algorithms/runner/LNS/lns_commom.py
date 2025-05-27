from typing import List, Dict, Callable

from algorithms.alns.lns import LNS
from algorithms.alns.stop.stop_condition import StopCondition, Interrupt
from algorithms.alns.acept_criterion.simulated_annealing import SimulatedAnnealing
from algorithms.alns.operators.operator_registry import OPERATOR_REGISTRY
from algorithms.alns.operators.operator_strategy import OperatorContext

import numpy as np


schema = [
    ("greedy_alpha", float, 0.1),
    ("destroy_factor", float, 0.5),
    ("method", str, "iteration"),
    ("limit", int, 5000),
    ("initial_temperature", int, 1),
    ("final_temperature", int, 1),
    ("cooling_rate", float, 0.95),
]


def get_config(destroy_operator: str, repair_operator: str) -> Dict:
    config = {
        "greedy_alpha": 0.15,
        "destroy_factor": 0.5,
        "method": "iteration",
        "limit": 5000,
        "initial_temperature": 25,
        "final_temperature": 1,
        "cooling_rate": 0.9975,
        "destroy_operator": destroy_operator,
        "repair_operator": repair_operator,
    }

    return config


def setup_lns(config) -> LNS:
    rng = np.random.default_rng()
    context = OperatorContext(
        rng=rng,
        greedy_alpha=config["greedy_alpha"],
        destroy_factor=config["destroy_factor"],
    )
    # destroy operators
    d_op = OPERATOR_REGISTRY[config["destroy_operator"]].get_instance_from_context(
        context
    )

    # repair operators
    r_op = OPERATOR_REGISTRY[config["repair_operator"]].get_instance_from_context(
        context
    )

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
    lns = LNS(
        stop=stop_by_iterations,
        accept=simulated_annealing,
        rng=rng,
        track_stats=True,
    )

    lns.destroy_operator = d_op
    lns.repair_operator = r_op

    return lns
