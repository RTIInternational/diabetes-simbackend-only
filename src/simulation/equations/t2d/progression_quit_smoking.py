from src.simulation.utils import *
from src.simulation.equations.models import *
from random import uniform

import numpy as np

EVENT = "quit_smoking"

FACTORS = {
    "lambda_val": -4.550,
    "shape": 0.3139614,
    "age_entry": 0.021,
    "female": -0.002,
    "black": -0.041,
    "hispanic": 0.341,
    "other_race": 0.690
}


def calculate_default(individual, step):
    explanators = 0
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS['black'] * individual['black']
    explanators += FACTORS['hispanic'] * individual['hispanic']
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['other_race'] * individual['other_race']

    shape = np.exp(FACTORS['shape'])

    integrated_hazard_t = weibull.model(explanators, step - 1, FACTORS['lambda_val'], shape)
    integrated_hazard_t1 = weibull.model(explanators, step, FACTORS['lambda_val'], shape)

    return 1 - np.exp(integrated_hazard_t - integrated_hazard_t1)


def calculate(individual, step, _, intervention, has_intervention):
    """predicts quitting"""

    # no need to update a non-smoker
    if get_event_in_step(individual, 'smoker', step - 1) == 0:
        return 0

    if intervention and has_intervention:
        intervention_data = intervention['smoking_control_intervention'][0]
        intervention_probability_quitting = intervention_data['probability of quitting']
    # no intervention is applied; current smoker will remain a smoker
    else:
        intervention_probability_quitting = 0

    probability_quitting = calculate_default(individual, step)

    complication_prob = probability_quitting + intervention_probability_quitting
    if complication_prob > 1:
        complication_prob = 1

    return rounder(complication_prob)


def modify_coefficients(data, rng):
    pass