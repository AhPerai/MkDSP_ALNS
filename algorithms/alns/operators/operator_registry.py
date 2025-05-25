from typing import Dict
from algorithms.alns.operators.operator_strategy import OperatorStrategy
from algorithms.alns.operators.repair_operators import (
    GreedyDegreeOperator,
    GreedyLeastDominatedOperator,
    GreedyHybridDominatedOperator,
    GreedyHybridDegreeOperator,
    RandomRepair,
)

from algorithms.alns.operators.destroy_operators import RandomDestroy


OPERATOR_REGISTRY: Dict[str, OperatorStrategy] = {
    RandomRepair.name: RandomRepair,
    GreedyDegreeOperator.name: GreedyDegreeOperator,
    GreedyLeastDominatedOperator.name: GreedyLeastDominatedOperator,
    GreedyHybridDegreeOperator.name: GreedyDegreeOperator,
    GreedyHybridDominatedOperator.name: GreedyDegreeOperator,
    RandomDestroy.name: RandomDestroy,
}
