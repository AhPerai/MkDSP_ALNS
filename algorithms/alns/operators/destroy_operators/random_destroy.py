from algorithms.alns.operators.operator_strategy import IOperatorStrategy


class RandomDestroy(IOperatorStrategy):

    def __init__(self, remove_value: int):
        super().__init__("random")
        self._remove_value = remove_value

    @property
    def remove_value(self) -> str:
        return self._remove_value

    def _modify_solution(self, current_solution):
        current_solution.S

    def _init_state_info(self, current_solution):
        pass

    def _update_state_info(self, current_solution):
        pass
