from src.simulation.utils import *
EVENT = "smoker"


def calculate(individual, step, _, intervention, has_intervention):

    # Assume that all non-smokers at baseline (FSMOKES=0) continue to be non-smokers in all subsequent periods
    # we just need to check previous time step because baseline non-smokers never start smoking
    if get_event_in_step(individual, 'smoker', step - 1) == 0:
        return 0
    # individual quits smoking in the current time step
    elif get_event_in_step(individual, 'quit_smoking', step) == 1:
        return 0
    else:
        # individual keeps smoking
        return 1


def modify_coefficients(data, rng):
    pass