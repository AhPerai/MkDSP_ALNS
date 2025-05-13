import os
import argparse
import algorithms.utils.result_logger as alns_logger

from algorithms.alns.alns import ALNS
from algorithms.solution_state import SolutionState
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


import objgraph


def setup_alns():
    #  fixed variables
    GREEDY_ALPHA = 0.15
    DESTROY_FACTOR = 0.5
    ITERATION = 10
    rng = np.random.default_rng()
    # BEST, NEW_BETTER, BETTER, ACCEPTED, NEW_ACCEPTED, REJECTED
    OUTCOME_REWARDS = [33, 0, 16, 0, 9, 0]

    # operators
    # repair
    random_repair_op = RandomRepair(rng)
    degree_repair_op = GreedyDegreeOperator(GREEDY_ALPHA)
    least_dom_repair_op = GreedyLeastDominatedOperator(GREEDY_ALPHA)
    hybrid_repair_op_v1 = GreedyHybridDominatedOperator(GREEDY_ALPHA)
    hybrid_repair_op_v2 = GreedyHybridDegreeOperator(GREEDY_ALPHA)
    # destroy
    destroy_op = RandomDestroy(DESTROY_FACTOR, rng)

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
        method=Interrupt.BY_ITERATION_LIMIT, limit=ITERATION
    )
    # acceptance criterion
    simulated_annealing = SimulatedAnnealing(
        initial_temperature=25, final_temperature=1, cooling_rate=0.998, rng=rng
    )
    # select strategy
    seg_roulette_wheel = RouletteWheelSelect(
        num_destroy_op=len(d_op_list),
        num_repair_op=len(r_op_list),
        segment_lenght=100,
        reaction_factor=0.5,
        outcome_rewards=OUTCOME_REWARDS,
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


def run_alns(alns_instance, path, k):
    initial_S = SolutionState(path, k)
    best_solution = alns_instance.execute(initial_S)

    TimeToBest = alns.stats.get_last_time_to_best()
    Runtime = alns.stats.get_runtime_duration()

    return {
        "ObjValue": len(best_solution.S),
        "TimeToBest": TimeToBest,
        "Runtime": Runtime,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run ALNS for a specific instance on a folder or for every instance in that folder"
    )
    parser.add_argument("--folder", type=str, required=True, help="folder path")
    parser.add_argument(
        "--instance",
        type=str,
        required=True,
        help="all for every instance in the folder\n instance file name for a specific instance;\nextensions: .txt | .graph",
    )
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument(
        "--runs", type=int, default=1, help="Number of runs per instance"
    )

    args = parser.parse_args()

    K = args.k
    RUNS = args.runs
    FOLDER = args.folder
    INSTANCE = args.instance
    alns = setup_alns()

    if INSTANCE != "all":
        instance_path = os.path.join(FOLDER, INSTANCE)
        instance_results = []

        for _ in range(RUNS):
            stats = run_alns(alns, instance_path, K)
            instance_results.append(stats)
            alns.reset()

        alns_logger.print_instance_results(INSTANCE, instance_results)

    else:
        results = {}

        for filename in os.listdir(FOLDER):
            if filename.endswith(".txt"):
                instance_path = os.path.join(FOLDER, filename)
                instance_results = []

                for _ in range(RUNS):
                    stats = run_alns(alns, instance_path, K)
                    instance_results.append(stats)
                    print(
                        f"finished:{filename} result:{stats["ObjValue"]}, duration: {stats["Runtime"]}"
                    )
                    alns.reset()

                results[filename] = instance_results

        for instance, result in results.items():
            alns_logger.print_instance_results(instance, result)
