import pprint
import numpy as np
from datetime import datetime
import csv
import json
import os


def eval_instance_results(instance, results):
    print(f"\n======== {instance} ========")
    solution_values = []
    ttb_time = []
    ttb_iteration = []
    runtime = []

    print(f"\n--- Results for each Run of {instance} ---\n")
    for i, instance_results in enumerate(results, 1):
        pprint.pprint(
            f"Run {i}: Solution Value: {instance_results["objective_value"]} | TtB: (Time: {instance_results["time_to_best"]:.2f} Iteration: {instance_results["iteration_to_best"]:.0f} | RunTime: {instance_results["runtime"]:.2f}"
        )
        solution_values.append(instance_results["objective_value"])
        runtime.append(instance_results["runtime"])
        ttb_iteration.append(instance_results["iteration_to_best"])
        ttb_time.append(instance_results["time_to_best"])

        best = min(solution_values)
        avg = np.mean(solution_values)
        std = np.std(solution_values)
        avg_time = np.mean(runtime)
        avg_time_to_best = np.mean(ttb_time)
        avg_iteration_to_best = np.mean(ttb_iteration)

        data = {
            "instance": instance,
            "best": best,
            "avg": round(avg, 2),
            "std": round(std, 2),
            "avg_time": round(avg_time, 2),
            "avg_time_to_best": round(avg_time_to_best, 2),
        }

    print(f"\n--- Average Results for {instance} ---")
    print(
        f"\nBest: {best} | Avg: {avg:.2f} | Std: {std:.2f} | Avg_Time: {avg_time:.2f} | Avg_Time_To_Bet: {avg_time_to_best:.2f} | Avg_Time_To_Best_IT: {avg_iteration_to_best:.0f}"
    )
    return data


def get_filename(algo, instance, k):
    algo_name = algo.__class__.__name__.lower()
    instance_name = instance.split(".")[0]
    timestamp = datetime.now().strftime("%d-%m-%Y-%H%M")
    filename = f"{algo_name}_k{k}_{instance_name}_{timestamp}"
    return filename


def create_folder(metaheuristic, folder_path: str, instance: str, k: int) -> str:
    algorithm_name = metaheuristic.__class__.__name__.upper()
    instance_name = instance.split(".")[0]
    instances_path = folder_path.split("/")[1]
    base_path = f"algorithms\\results\\{algorithm_name}\\results"

    # Get the last file_number adds 1 and pads with 0s
    folders = [
        f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))
    ]
    folders.sort()
    number_id = "001"
    if folders:
        last_folder = folders[-1]
        prefix = last_folder.split("_")[0]
        number_id = f"{int(prefix) + 1:03d}"

    new_folder = f"{number_id}_{instances_path}_{instance_name}-K_{k}"
    full_path = f"{base_path}\\{new_folder}"
    os.makedirs(full_path, exist_ok=True)
    return full_path


def add_config_file(config: dict, folder):
    filepath = os.path.join(folder, "config.json")

    with open(filepath, "w") as file:
        json.dump(config, file, indent=2)

    return filepath


def add_progression_log(folder, progression_metrics):
    pass


def add_metrics(folder, data):
    filepath = os.path.join(folder, "data")

    file_exists = os.path.isfile(filepath)
    with open(filepath, mode="a", newline="") as csvfile:
        fieldnames = list(data.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
