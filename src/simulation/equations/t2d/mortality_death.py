from src.simulation.utils import *

EVENT = "death"

IS_TERMINAL = True


def calculate(individual, step, *_):
    """
        Calculate aggregate death. This equation is dependent on cvd_death and
        non_cvd_death
        """
    if (
            has_event_in_step(individual, 'current_cvd_death', step) or
            has_event_in_step(individual, 'ever_cvd_death', step) or
            has_event_in_step(individual, 'non_cvd_death', step) or
            individual['age'] > 98
    ):
        return 1

    return 0


def modify_coefficients(data, rng):
    pass