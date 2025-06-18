import os
import argparse
import objgraph
import algorithms.utils.metrics_logger as metrics_logger
from algorithms.runner.lns.lns_commom import setup_lns, get_config
from algorithms.alns.lns import LNS
from algorithms.solution_state import SolutionState
import numpy.random as random


from algorithms.alns.operators.repair_operators import (
    GreedyDegreeOperator,
    GreedyLeastDominatedOperator,
    GreedyHybridDominatedOperator,
    GreedyHybridDegreeOperator,
    RandomRepair,
)

from algorithms.alns.operators.destroy_operators.random_destroy import RandomDestroy


def run_lns_metrics(config, k, folder, runs):
    algorithm_name = LNS.__name__
    metrics_folder = metrics_logger.create_folder(
        algorithm_name,
        folder,
        "all",
        k,
        config["destroy_operator"],
        config["repair_operator"],
    )
    metrics_logger.add_config_file(config, folder=metrics_folder)

    for filename in os.listdir(folder):
        instance = os.path.join(folder, filename)
        initial_S = SolutionState(instance, k)
        lns = setup_lns(config)

        instance_results = []
        best_run_value = float("inf")
        best_run_progression_metric = {}

        for _ in range(runs):
            copy_S = initial_S.copy()
            solution = lns.execute(copy_S)
            run_results = {
                "objective_value": len(solution.S),
                "runtime": lns.stats.get_runtime_duration(),
                "time_to_best": lns.stats.get_last_time_to_best()[2],
                "iteration_to_best": lns.stats.get_last_time_to_best()[1],
            }
            instance_results.append(run_results)
            if run_results["objective_value"] < best_run_value:
                best_run_value = run_results["objective_value"]
                best_run_progression_metric = lns.stats.get_metrics()

            lns.reset(random.default_rng())

        metrics_logger.add_progression_log(
            metrics_folder, filename, best_run_progression_metric, algorithm_name
        )
        row_data = metrics_logger.eval_instance_results(filename, instance_results)
        metrics_logger.add_metrics(metrics_folder, row_data)


import pprint

if __name__ == "__main__":
    instances_path = os.path.join("instances", "cities_small_instances")
    K_values = [1, 2, 4]
    repair_operators = [
        RandomRepair.name,
    ]
    destroy_operators = [RandomDestroy.name]

    pprint.pprint(repair_operators)
    pprint.pprint(destroy_operators)
    for destroy_operator_name in destroy_operators:
        for repair_operator_name in repair_operators:
            config = get_config(destroy_operator_name, repair_operator_name)
            print(
                f"\n\nOPERATORS:  DESTROY:{destroy_operator_name} REPAIR:{repair_operator_name}\n\n"
            )
            for K in K_values:
                print(f"\n\nINITIALIZING FOR K ={K}\n\n")
                run_lns_metrics(config, K, instances_path, 3)
