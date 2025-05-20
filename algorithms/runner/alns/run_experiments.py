import os
import argparse
import objgraph
import algorithms.utils.metrics_logger as metrics_logger
from algorithms.runner.alns.alns_commom import setup_alns, get_config
from algorithms.alns.alns import ALNS
from algorithms.solution_state import SolutionState


def run_alns_metrics(config, k, folder, runs):
    algorithm_name = ALNS.__name__
    metrics_folder = metrics_logger.create_folder(algorithm_name, folder, "all", k)
    metrics_logger.add_config_file(config, folder=metrics_folder)

    results = {}

    for filename in os.listdir(folder):
        instance = os.path.join(folder, filename)
        initial_S = SolutionState(instance, k)
        alns = setup_alns(config)

        instance_results = []
        best_run_value = float("inf")
        best_run_progression_metric = {}

        for _ in range(runs):
            solution = alns.execute(initial_S)
            run_results = {
                "objective_value": len(solution.S),
                "runtime": alns.stats.get_runtime_duration(),
                "time_to_best": alns.stats.get_last_time_to_best()[2],
                "iteration_to_best": alns.stats.get_last_time_to_best()[1],
            }
            instance_results.append(run_results)
            if run_results["objective_value"] < best_run_value:
                best_run_progression_metric = alns.stats.get_metrics()

            alns.reset()

        metrics_logger.add_progression_log(
            metrics_folder, filename, best_run_progression_metric
        )
        row_data = metrics_logger.eval_instance_results(filename, instance_results)
        metrics_logger.add_metrics(metrics_folder, row_data)


import pprint

if __name__ == "__main__":
    config = get_config()
    instances_path = os.path.join("instances", "cities_small_instances")
    run_alns_metrics(config, 2, instances_path, 1)
