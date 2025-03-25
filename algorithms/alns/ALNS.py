import warnings


class ALNS:

    def __init__(self):
        self._destroy_operators = dict()
        self._repair_operators = dict()

    def execute():
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

    @staticmethod
    def _add_operator(operator, operator_list, operator_name=None):
        if operator_name is None:
            name = operator.__name__

        if name in operator_list:
            warnings.warn("oi")

        operator_list[name] = operator
