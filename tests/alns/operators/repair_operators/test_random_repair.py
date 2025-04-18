import pytest

from algorithms.alns.operators.repair_operators.random_repair import (
    RandomRepair,
)
from tests.utils.valid_solution_assertions import (
    validate_operator_solution_dominates_graph,
    validate_operator_generate_valid_solution,
)


@pytest.mark.parametrize("operator_class", [RandomRepair])
@pytest.mark.parametrize(
    "instance_path,K", [("instances/cities_small_instances/york.txt", 2)]
)
def test_random_repair_operator_generate_valid_solution(
    operator_class, instance_path, K
):
    validate_operator_generate_valid_solution(operator_class, instance_path, K)


@pytest.mark.parametrize("operator_class", [RandomRepair])
@pytest.mark.parametrize(
    "instance_path,K", [("instances/cities_small_instances/york.txt", 2)]
)
def test_random_repair_operator_dominates_graph(operator_class, instance_path, K):
    validate_operator_solution_dominates_graph(operator_class, instance_path, K)
