from src.simulation.utils import *

EVENT = "overall_cost"

IS_DETERMINISTIC = True


def calculate(individual, step, *_):
    """
    Calculate aggregate cvd based on the occurrence of one of the qualifying CVD events during the current step only.
    """
    overall_cost = 0
    overall_cost += get_event_in_step(individual, 'health_cost', step)
    overall_cost += get_event_in_step(individual, 'event_cost', step)
    overall_cost += get_event_in_step(individual, 'intervention_cost', step)

    return overall_cost


def modify_coefficients(data, rng):
    pass