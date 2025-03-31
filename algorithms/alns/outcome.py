from enum import Enum


class Outcome(Enum):
    BEST = (1, 33)
    NEW_BETTER = (2, 17)
    BETTER = (3, 9)
    NEW_ACCEPTED = (4, 13)
    ACCEPTED = (5, 7)
    REJECTED = (6, 0)

    def __init__(self, id, reward):
        self.id = id
        self.reward = reward
