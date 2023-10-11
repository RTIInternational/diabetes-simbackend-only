from src.simulation.utils import *

EVENT = "bmi"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 2.197179,
    "lag_value": 0.902067,
    "step": -0.381378,
    "initial_value": 0.075748,
    "female": -0.063124,
    "black": -0.022505,
    "hispanic": -0.049535,
    "age_entry": -0.012278,
    "diabetes_duration_entry": 0.002443,
    "has_postsecondary_ed": -0.050545,
    "la_trial": -0.096119,
    "intensive_la_treatment": 0.108875
}


def calculate(individual, step, *_):

    explanators = 0
    explanators += FACTORS["lag_value"] * get_event_in_step(individual, 'bmi', step - 1)
    explanators += FACTORS["step"] * math.log(step)
    explanators += FACTORS["initial_value"] * get_event_in_step(individual, 'bmi', 0)
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS['black'] * individual['black']
    explanators += FACTORS['hispanic'] * individual['hispanic']
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['la_trial'] * individual['la_trial']
    explanators += FACTORS['has_postsecondary_ed'] * individual['has_postsecondary_ed']
    explanators += FACTORS['intensive_la_treatment'] * individual['intensive_la_treatment']

    progression = explanators + FACTORS['intercept']

    return rounder(progression)


def modify_coefficients(data, rng):
    pass