import pprint
import numpy as np
from typing import List
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


def create_folder(
    metaheuristic_name,
    folder_path: str,
    instance: str,
    k: int,
    destroy_op_name: str = None,
    repair_op_name: str = None,
) -> str:
    operators = (destroy_op_name, repair_op_name)
    instance_name = instance.split(".")[0]
    instances_path_name = os.path.basename(folder_path)
    base_path = f"algorithms\\runner\\{metaheuristic_name.lower()}\\metrics"

    if metaheuristic_name.lower() == "lns" and operators:
        base_path = f"{base_path}\\{destroy_op_name}\\{repair_op_name}"
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    print(base_path)

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


def _add_operators_progression(metrics, metaheuristic_name):
    if metaheuristic_name.lower() == "lns":
        return None

    op_progression = {}
    op_progression.update(metrics["d_op_progression"])
    op_progression.update(metrics["r_op_progression"])

    records = {}
    for op_name, lists in op_progression.items():
        data = lists[0]
        steps = len(data["attempt"])
        for metric in ("attempt", "score", "weight"):
            for idx in range(steps):
                col = (metric, idx)
                records.setdefault(op_name, {})[col] = data[metric][idx]

    df_ops = pd.DataFrame.from_dict(records, orient="index")

    df_ops = df_ops.reindex(sorted(df_ops.columns, key=lambda x: (x[1], x[0])), axis=1)
    df_ops.columns = pd.MultiIndex.from_tuples(
        df_ops.columns, names=["Metric", "Update"]
    )

    df_ops.columns = df_ops.columns.swaplevel(0, 1)

    df_ops = df_ops.sort_index(axis=1, level=0)
    return df_ops


def add_progression_log(
    base_folder: str, instance_name: str, metrics: dict, metaheuristic_name: str
):
    progression_folder = os.path.join(base_folder, "progression")
    os.makedirs(progression_folder, exist_ok=True)

    file_path = os.path.join(progression_folder, f"{instance_name}_progression.xlsx")

    best_prog = metrics["best_solution_progression"]
    df_best = pd.DataFrame(
        best_prog, columns=["SolutionSize", "Iteration", "TimeElapsed", "Operator"]
    )

    df_ops = _add_operators_progression(metrics, metaheuristic_name)

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_best.to_excel(writer, sheet_name="Best Progression", index=False)
        if df_ops is not None:
            df_ops.to_excel(writer, sheet_name="Operator Progression")

    print(f"Progression log written to: {file_path}")


def add_metrics(folder, data):
    filepath = os.path.join(folder, "data.csv")

    file_exists = os.path.isfile(filepath)
    with open(filepath, mode="a", newline="") as csvfile:
        fieldnames = list(data.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def create_excel_from_results(root_folder):
    output_file = os.path.join(root_folder, "Resultados_Experimentais.xlsx")

    writer = pd.ExcelWriter(output_file, engine="openpyxl")

    # Especifica as
    for folder_name in ["alns_conf_k_1", "alns_conf_k_2", "alns_conf_k_4"]:
        folder_path = os.path.join(root_folder, folder_name)
        if not os.path.exists(folder_path):
            continue

        sheet_data = {}
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder)
            if not os.path.isdir(subfolder_path):
                continue

            k_value = subfolder.split("-K_")[-1]

            data_path = os.path.join(subfolder_path, "data.csv")
            if os.path.isfile(data_path):
                df = pd.read_csv(data_path)
                sheet_data[k_value] = df

        if sheet_data:
            sheet_df = pd.concat(sheet_data, axis=1)
            sheet_df.to_excel(writer, sheet_name=folder_name)

    # Tratamento especifico para a pasta do lns já que possui vários algoritmos
    lns_folder = os.path.join(root_folder, "lns")
    if os.path.exists(lns_folder):
        for destroy_op in os.listdir(lns_folder):
            destroy_path = os.path.join(lns_folder, destroy_op)
            if not os.path.isdir(destroy_path):
                continue

            for repair_op in os.listdir(destroy_path):
                repair_path = os.path.join(destroy_path, repair_op)
                if not os.path.isdir(repair_path):
                    continue

                sheet_name = f"{destroy_op}_{repair_op}"[:31]

                sheet_data = {}
                for subfolder in os.listdir(repair_path):
                    subfolder_path = os.path.join(repair_path, subfolder)
                    if not os.path.isdir(subfolder_path):
                        continue

                    k_value = subfolder.split("-K_")[-1]

                    data_path = os.path.join(subfolder_path, "data.csv")
                    if os.path.isfile(data_path):
                        df = pd.read_csv(data_path)
                        sheet_data[k_value] = df

                if sheet_data:
                    sheet_df = pd.concat(sheet_data, axis=1)
                    sheet_df.to_excel(writer, sheet_name=sheet_name)

    writer.close()
    print(f"Folha de Experimentos criada em: {output_file}")


if __name__ == "__main__":
    create_excel_from_results(f"D:\\Users\\Pera\Desktop\\124 - Novos Testes")
