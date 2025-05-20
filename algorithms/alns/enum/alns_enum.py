from enum import Enum


class Outcome(Enum):
    BEST = (0, "BEST")
    NEW_BETTER = (1, "NEW_BETTER")
    BETTER = (2, "BETTER")
    NEW_ACCEPTED = (3, "NEW_ACCEPTED")
    ACCEPTED = (4, "ACCEPTED")
    REJECTED = (5, "REJECTED")

    def __init__(self, id, label):
        self.id = id
        self.label = label


class OperatorType(Enum):
    DESTROY = 1
    REPAIR = 2
