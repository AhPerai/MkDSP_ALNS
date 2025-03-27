from typing import Dict, List, Tuple


class ALNS:

    def __init__(self):
        self._destroy_operators = {}
        self._repair_operators = {}

    def execute(
        self,
    ):
        """
        blank comment
        """
        pass

    def select_operator():
        NotImplementedError

    def repair_operators():
        NotImplementedError

    def destroy_operators():
        NotImplementedError

    def add_destroy_operator(self, operator, name=None):
        self._add_operator(self._destroy_operators, operator, name)

    def add_repair_operator(self, operator, name=None):
        self._add_operator(self._repair_operators, operator, name)
