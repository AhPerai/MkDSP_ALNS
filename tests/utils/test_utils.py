def assert_state_equal(S_updated, S_expected, i, SEED):
    assert S_updated.S == S_expected.S, (
        f"[FAIL] Iteration {i} | SEED {SEED} | Solution sets differ.\n"
        f"S_updated.S: {S_updated.S}\nS_expected.S: {S_expected.S}"
    )
    assert S_updated.dominated == S_expected.dominated, (
        f"[FAIL] Iteration {i} | SEED {SEED} | Dominated sets differ.\n"
        f"S_updated.dominated: {S_updated.dominated}\n"
        f"S_expected.dominated: {S_expected.dominated}"
    )
    assert S_updated.non_dominated == S_expected.non_dominated, (
        f"[FAIL] Iteration {i} | SEED {SEED} | Non-dominated sets differ.\n"
        f"S_updated.non_dominated: {S_updated.non_dominated}\n"
        f"S_expected.non_dominated: {S_expected.non_dominated}"
    )
