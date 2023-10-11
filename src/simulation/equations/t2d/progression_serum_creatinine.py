from src.simulation.utils import *

EVENT = "serum_creatinine"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 0.002537,
    "lag_value": 0.960606,
    "step": 0.003947,
    "initial_value": 0.035205,
    "female": -0.005074,
    "black": 0.004441,
    "hispanic": -0.000071,
    "age_entry": 0.000315,
    "diabetes_duration_entry": 0.000612,
    "has_postsecondary_ed": -0.003326,
    "la_trial": -0.006863,
    "intensive_la_treatment": 0.008780,
    "serum_creatinine_treatment": -0.009767
}


def calculate(individual, step, *_):

    explanators = 0
    explanators += FACTORS["lag_value"] * get_event_in_step(individual, 'serum_creatinine', step - 1)
    explanators += FACTORS["step"] * math.log(step)
    explanators += FACTORS["initial_value"] * get_event_in_step(individual, 'serum_creatinine', 0)
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS['black'] * individual['black']
    explanators += FACTORS['hispanic'] * individual['hispanic']
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['la_trial'] * individual['la_trial']
    explanators += FACTORS['has_postsecondary_ed'] * individual['has_postsecondary_ed']
    explanators += FACTORS['intensive_la_treatment'] * individual['intensive_la_treatment']
    explanators += FACTORS['serum_creatinine_treatment'] * individual['serum_creatinine_treatment']

    progression = explanators + FACTORS['intercept']

    return rounder(progression)


def modify_coefficients(data, rng):
    pass