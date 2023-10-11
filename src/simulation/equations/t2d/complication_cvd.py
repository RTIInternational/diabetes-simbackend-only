from src.simulation.utils import *

EVENT = "cvd"


def calculate(individual, step, *_):
    """
    Calculate aggregate cvd based on the occurrence of one of the qualifying CVD events during the current step only.
    """
    if (
        has_event_in_step(individual, 'mi', step) or
        has_event_in_step(individual, 'chf', step) or
        has_event_in_step(individual, 'stroke', step) or
        has_event_in_step(individual, 'revasc', step) or
        has_event_in_step(individual, 'angina', step)
    ):
        return 1

    return 0


def modify_coefficients(data, rng):
    pass