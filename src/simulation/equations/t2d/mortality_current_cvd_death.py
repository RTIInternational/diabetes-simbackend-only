from src.simulation.utils import *
from src.simulation.equations.models import *
from copy import deepcopy

EVENT = "current_cvd_death"

FACTORS = {
    "intercept": [-7.824, 0.839],
    "female": [-0.231, 0.136],
    "black": [-0.405, 0.179],
    "other": [-0.426, 0.241],
    "accord": [0.324, 0.139],
    "twd_hba1c": [0.166, 0.061],
    "twd_serum_creatinine": [0.808, 0.213],
    "current_stroke": [0.946, 0.152],
    "current_mi": [1.091, 0.120],
    "current_chf": [2.124, 0.123],
    "current_angina": [-0.250, 0.149],
    "current_age": [0.030, 0.008]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, *_):
    """
    Calculate probability of death only if individual has had an event in the current step
    """

    if not has_event_in_step(individual, 'cvd', step):
        return 0

    explanators = 0
    explanators += FACTORS['female'][0] * individual['female']
    explanators += FACTORS['black'][0] * individual['black']
    explanators += FACTORS['other'][0] * individual['other_race']
    explanators += FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += FACTORS['twd_serum_creatinine'][0] * time_weighted_risk_factor(individual, 'serum_creatinine')
    explanators += FACTORS['current_age'][0] * individual['age']

    if individual['accord'] == 1:
        explanators += FACTORS['accord'][0]

    if has_event_in_step(individual, 'angina', step):
        explanators += FACTORS['current_angina'][0]
    if has_event_in_step(individual, 'stroke', step):
        explanators += FACTORS['current_stroke'][0]
    if has_event_in_step(individual, 'mi', step):
        explanators += FACTORS['current_mi'][0]
    if has_event_in_step(individual, 'chf', step):
        explanators += FACTORS['current_chf'][0]

    mortality_multipliers = custom_values['mortality_multipliers']
    multiplier = mortality_multipliers['Equation 2']

    progression_prob = logistic.model(explanators, FACTORS['intercept'][0])
    progression_prob = min(multiplier * progression_prob, 1)

    return rounder(progression_prob)


def modify_coefficients(data, rng):
    psa_factor = data
    global MODIFIED_FACTORS
    if psa_factor:
        modified_factors_dict = {}
        for factor, value in FACTORS.items():
            new_value = normal.model(rng, value[0], value[1], 4)
            modified_factors_dict[factor] = [new_value]
        MODIFIED_FACTORS = modified_factors_dict

