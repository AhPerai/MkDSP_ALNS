import pprint
import numpy as np
from datetime import datetime
import csv
import json
import os
import pandas as pd


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


def create_folder(metaheuristic_name, folder_path: str, instance: str, k: int) -> str:
    instance_name = instance.split(".")[0]
    instances_path_name = os.path.basename(folder_path)
    base_path = f"algorithms\\runner\\{metaheuristic_name.lower()}\\metrics"

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

    new_folder = f"{number_id}_{instances_path_name}_{instance_name}-K_{k}"
    full_path = f"{base_path}\\{new_folder}"
    os.makedirs(full_path, exist_ok=True)
    return full_path


def add_config_file(config: dict, folder: str):
    filepath = os.path.join(folder, "config.json")

    with open(filepath, "w") as file:
        json.dump(config, file, indent=2)

    return filepath


def add_progression_log(base_folder: str, instance_name: str, metrics: dict):
    """
    Writes an Excel file with two sheets:
      1) Best-solution progression
      2) Operator progression (destroy + repair) in wide format

    Args:
      base_folder: Path to instance-specific folder.
      instance_name: Name of the instance (used in filename).
      metrics: dict returned by get_alns_metrics().
    """
    progression_folder = os.path.join(base_folder, "progression")
    os.makedirs(progression_folder, exist_ok=True)
    # Prepare file path
    file_path = os.path.join(progression_folder, f"{instance_name}_progression.xlsx")

    # 1) Best-solution progression
    best_prog = metrics["best_solution_progression"]
    df_best = pd.DataFrame(
        best_prog, columns=["SolutionSize", "Iteration", "TimeElapsed", "Operator"]
    )

    # 2) Operator progression
    # Combine destroy and repair into one dict
    op_progression = {}
    op_progression.update(metrics["d_op_progression"])
    op_progression.update(metrics["r_op_progression"])

    # Build multi-index columns: (metric, update_idx)
    records = {}
    for op_name, lists in op_progression.items():
        # lists is a list of one dict containing attempt, score, weight lists
        data = lists[0]
        steps = len(data["attempt"])
        for metric in ("attempt", "score", "weight"):
            for idx in range(steps):
                col = (metric, idx)
                records.setdefault(op_name, {})[col] = data[metric][idx]

    # Create DataFrame
    df_ops = pd.DataFrame.from_dict(records, orient="index")
    # Sort columns by metric, then step
    df_ops = df_ops.reindex(sorted(df_ops.columns, key=lambda x: (x[0], x[1])), axis=1)
    df_ops.columns = pd.MultiIndex.from_tuples(
        df_ops.columns, names=["Metric", "Update"]
    )
    df_ops.columns = df_ops.columns.swaplevel(0, 1)

    # Write to Excel with two sheets
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_best.to_excel(writer, sheet_name="Best Progression", index=False)
        df_ops.to_excel(writer, sheet_name="Operator Progression")

    print(f"Progression log written to: {file_path}")


def add_metrics(folder, data):
    filepath = os.path.join(folder, "data")

    file_exists = os.path.isfile(filepath)
    with open(filepath, mode="a", newline="") as csvfile:
        fieldnames = list(data.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
