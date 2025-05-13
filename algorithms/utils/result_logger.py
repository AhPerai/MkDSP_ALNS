import pprint
import numpy as np
import csv


def print_instance_results(instance, results):
    print(f"\n======== {instance} ========")
    solution_values = []
    ttb_time = []
    ttb_iteration = []
    runtime = []

    print(f"\n--- Results for each Run of {instance} ---\n")
    for i, instance_results in enumerate(results, 1):
        pprint.pprint(
            f"Run {i}: Solution Value: {instance_results["ObjValue"]} | TtB: (Time: {instance_results["TimeToBest"][2]:.2f} Iteration: {instance_results["TimeToBest"][1]:.0f} | RunTime: {instance_results["Runtime"]:.2f}"
        )
        solution_values.append(instance_results["ObjValue"])
        runtime.append(instance_results["Runtime"])
        ttb_iteration.append(instance_results["TimeToBest"][1])
        ttb_time.append(instance_results["TimeToBest"][2])

        best = min(solution_values)
        avg = np.mean(solution_values)
        std = np.std(solution_values)

        avg_time = np.mean(runtime)
        avg_time_to_best = np.mean(ttb_time)
        avg_iteration_to_best = np.mean(ttb_iteration)
    print(f"\n--- Average Results for {instance} ---")
    print(
        f"\nBest: {best} | Avg: {avg:.2f} | Std: {std:.2f} | Avg_Time: {avg_time:.2f} | Avg_Time_To_Bet: {avg_time_to_best:.2f} | Avg_Time_To_Best_IT: {avg_iteration_to_best:.0f}"
    )
