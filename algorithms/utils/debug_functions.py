import numpy.random as random
from algorithms.solution_state import Index
import numpy as np


def debug_state_difference(
    given_solution,
    expected_solution,
    i,
    SEED,
    info_to_check=None,
    nodes_to_check=None,
):
    print(
        f"\n[DEBUG] Iteration {i} | SEED {SEED} | Checking solution state differences"
    )

    if given_solution.S != expected_solution.S:
        diff = given_solution.S ^ expected_solution.S
        print(f"[DIFF] Solution sets differ:\n  Symmetric difference: {diff}")
    else:
        print("[OK] Solution sets match.")

    if given_solution.dominated != expected_solution.dominated:
        only_in_given = given_solution.dominated - expected_solution.dominated
        only_in_expected = expected_solution.dominated - given_solution.dominated
        print("[DIFF] Dominated sets differ:")
        print(f"  In given but not expected: {only_in_given}")
        print(f"  In expected but not given: {only_in_expected}")
    else:
        print("[OK] Dominated sets match.")

    if given_solution.non_dominated != expected_solution.non_dominated:
        diff = given_solution.non_dominated ^ expected_solution.non_dominated
        print(f"[DIFF] Non-dominated sets differ:\n  Symmetric difference: {diff}")
    else:
        print("[OK] Non-dominated sets match.")

    if nodes_to_check is None:
        nodes_to_check = expected_solution.G.nodes()

    if info_to_check is None:
        info_to_check = [Index.K]

    count = 0
    for v in nodes_to_check:
        for index in info_to_check:
            val_given = given_solution.G_info[v][index]
            val_expected = expected_solution.G_info[v][index]
            if val_given != val_expected:
                print(f"[DIFF] Node {v} differs at Index.{index.name}:")
                print(f"  Given   : {val_given}")
                print(f"  Expected: {val_expected}")
                count += 1

    print(
        f"[SUMMARY] {count}/{len(nodes_to_check)} nodes had mismatching info for checked indices."
    )


def find_rng_matching_expected_uniform_value(percentages_list, iterations=10):
    seed_list = []
    for _ in range(iterations):
        rng = random.default_rng(_)
        count = 0
        for i in range(3):
            random_percent = rng.uniform(0, 1)
            if percentages_list[i][0] <= random_percent <= percentages_list[i][1]:
                count += 1

        if count == 3:
            print(f"seed:{_}")
            seed_list.append(_)
    return seed_list


def find_choice_seed_for_index(index_to_match, num_operators=4, tries=100):
    for seed in range(tries):
        rng = np.random.default_rng(seed)
        weights = np.ones(num_operators)
        probabilities = weights / np.sum(weights)
        first_choice = rng.choice(num_operators, p=probabilities)
        second_choice = rng.choice(num_operators, p=probabilities)

        if first_choice == index_to_match and second_choice == index_to_match:
            print(f"Seed {seed} produces choice {first_choice} and {second_choice}")
            yield seed


if __name__ == "__main__":
    find_rng_matching_expected_uniform_value([(0, 0.6), (0.37, 1), (0, 0.6)])
