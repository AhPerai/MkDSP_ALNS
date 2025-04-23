from enum import Enum


class Outcome(Enum):
    BEST = (1, 24, "BEST")
    NEW_BETTER = (2, 17, "NEW_BETTER")
    BETTER = (3, 9, "BETTER")
    NEW_ACCEPTED = (4, 13, "NEW_ACCEPTED")
    ACCEPTED = (5, 7, "ACCEPTED")
    REJECTED = (6, 0, "REJECTED")

    def __init__(self, id, reward, label):
        self.id = id
        self.reward = reward
        self.label = label
