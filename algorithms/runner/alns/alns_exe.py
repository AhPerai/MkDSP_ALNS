#!/usr/bin/env python3
from algorithms.runner.alns.alns_commom import schema, setup_alns, get_config_from_args
from algorithms.solution_state import SolutionState
import argparse


def run_alns() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", type=str, required=True, help="Instance file path")
    parser.add_argument("-k", type=int, default=2, help="Value of k")
    for key, caster, default in schema:
        parser.add_argument(f"--{key}", type=caster, default=default)
    args = parser.parse_args()

    instance = args.f
    k = args.k

    config = get_config_from_args(args)

    initial_S = SolutionState(instance, k)
    alns = setup_alns(config)

    solution = alns.execute(initial_S)
    objective_val = len(solution.S)
    alns.clear()
    content = f"instance: {instance} - {k} | result: {objective_val}"
    print(content)


if __name__ == "__main__":
    run_alns()
