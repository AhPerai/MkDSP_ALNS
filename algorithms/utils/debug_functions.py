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
