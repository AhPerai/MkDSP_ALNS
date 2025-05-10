from enum import Enum
from typing import Dict, List, Callable
from algorithms.alns.outcome import Outcome
from algorithms.solution_state import SolutionState
from algorithms.alns.operators.operator_strategy import OperatorStrategy


class Event(Enum):
    ON_ANY_OUTCOME = (0, "FOUND_SOLUTION")
    ON_BEST = (1, "FOUND_BEST")
    ON_BETTER = (2, "FOUND_BETTER")
    ON_ACCEPTED = (3, "FOUND_ACCEPTED")
    ON_REJECTED = (4, "FOUND_REJECTED")
    ON_SELECT = (5, "ON_SELECTION")
    ON_SELECT_UPDATE = (6, "ON_SELECT_UPDATE")
    ON_END = (1, "END")

    def __init__(self, id, label):
        self.id = id
        self.label = label

    @classmethod
    def get_event_by_outcome(cls, outcome: Outcome) -> "Event":
        return _OUTCOME_TO_EVENT.get(outcome, None)

    @classmethod
    def get_event_outcome_list(cls) -> List["Event"]:
        return [Event.ON_BEST, Event.ON_BETTER, Event.ON_ACCEPTED, Event.ON_REJECTED]


_OUTCOME_TO_EVENT: Dict[Outcome, Event] = {
    Outcome.BEST: Event.ON_BEST,
    Outcome.BETTER: Event.ON_BETTER,
    Outcome.ACCEPTED: Event.ON_ACCEPTED,
    Outcome.REJECTED: Event.ON_REJECTED,
}


class EventHandler:

    def __init__(self):
        self._listeners: Dict[Event, List[Callable]] = {}

    def is_event_empty(self, event: Event):
        return not self._listeners.get(event, [])

    def __add_listener(self, event: Event, callback: Callable):
        if event not in self._listeners:
            self._listeners[event] = []

        self._listeners[event].append(callback)

    def register(self, event: Event, callback: Callable):
        if event == Event.ON_ANY_OUTCOME:
            for outcome_event in Event.get_event_outcome_list():
                self.__add_listener(outcome_event, callback)
            return

        self.__add_listener(event, callback)

    def trigger(self, event: Event, *args, **kwargs):
        if not self.is_event_empty(event):
            for callback in self._listeners.get(event):
                callback(*args, **kwargs)

    def on_outcome(self, outcome: Outcome, solution: SolutionState, operator_name: str):
        event = Event.get_event_by_outcome(outcome)
        if event:
            self.trigger(event, solution, operator_name)

    def unregister_all(self):
        self._listeners.clear()
