import os
import argparse
import objgraph
import algorithms.utils.metrics_logger as metrics_logger
from algorithms.runner.lns.lns_commom import setup_alns, get_config
from algorithms.alns.lns import LNS
from algorithms.solution_state import SolutionState


def run_lns_metrics(config, k, folder, runs):
    algorithm_name = LNS.__name__
    metrics_folder = metrics_logger.create_folder(algorithm_name, folder, "all", k)
    metrics_logger.add_config_file(config, folder=metrics_folder)

    for filename in os.listdir(folder):
        instance = os.path.join(folder, filename)
        initial_S = SolutionState(instance, k)
        lns = setup_lns(config)

        instance_results = []
        best_run_value = float("inf")
        best_run_progression_metric = {}

        for _ in range(runs):
            solution = lns.execute(initial_S)
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

            lns.reset()

        metrics_logger.add_metrics(
            metrics_folder, filename, best_run_progression_metric
        )
        row_data = metrics_logger.eval_instance_results(filename, instance_results)
        metrics_logger.add_metrics(metrics_folder, row_data)


import pprint

if __name__ == "__main__":
    config = get_config()
    instances_path = os.path.join("instances", "cities_small_instances")
    K_values = [1, 2, 4]
    repair_operators = [
        "",
        "",
    ]
    for K in K_values:
        print(f"\n\nINITIALIZING FOR K ={K}\n\n")
        run_lns_metrics(config, K, instances_path, 5)
