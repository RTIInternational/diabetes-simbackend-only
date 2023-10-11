from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "stroke"

FACTORS = {
    "intercept": [-15.348, 0.726],
    "shape": [0.225, 0.035],
    "age_entry": [0.045, 0.006],
    "has_postsecondary_ed": [-0.160, 0.086],
    "female": [-0.180, 0.081],
    "hispanic": [-0.231, 0.146],
    "accord": [0.180, 0.089],
    "curr_smoker": [0.276, 0.132],
    "twd_sbp": [0.023, 0.003],
    "twd_ldl": [0.007, 0.001],
    "twd_hba1c": [0.247, 0.039],
    "twd_trig": [0.167, 0.077],
    "lagged_micro": [0.187, 0.080],
    "lagged_dialysis": [0.513, 0.206],
    "ever_revasc": [0.282, 0.092],
    "ever_stroke": [1.054, 0.107],
    "ever_mi": [0.338, 0.098],
    "ever_chf": [0.613, 0.123]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of stroke
    """
    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['has_postsecondary_ed'][0] * individual['has_postsecondary_ed']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['hispanic'][0] * individual['hispanic']

    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_ldl'][0] * time_weighted_risk_factor(individual, 'ldl')

    if individual['accord'] == 1:
        explanators += MODIFIED_FACTORS['accord'][0]

    if get_event_in_step(individual, 'smoker', step):
        explanators += MODIFIED_FACTORS['curr_smoker'][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_micro'][0]

    if has_history(individual, 'dialysis', step):
        explanators += MODIFIED_FACTORS['lagged_dialysis'][0]

    if has_history(individual, 'revasc', step):
        explanators += MODIFIED_FACTORS['ever_revasc'][0]

    if has_history(individual, 'stroke', step):
        explanators += MODIFIED_FACTORS['ever_stroke'][0]

    if has_history(individual, 'mi', step):
        explanators += MODIFIED_FACTORS['ever_mi'][0]

    if has_history(individual, 'chf', step):
        explanators += MODIFIED_FACTORS['ever_chf'][0]

    total_risk_reduction = 0
    if intervention and is_intervention:
        risk_reductions = intervention['risk reductions']
        count = 1
        for intervent, reduction in risk_reductions.items():
            reduction = abs(reduction)
            if intervent == 'bp_control_intervention':
                if get_event_in_step(individual, 'sbp', step) > intervention['sbp_condition']:
                    total_risk_reduction += math.pow(reduction, count)
                    count += 1
            elif intervent == 'cholesterol_control_intervention':
                if individual['age'] >= intervention['cholesterol min age']:
                    total_risk_reduction += math.pow(reduction, count)
                    count += 1
            else:
                total_risk_reduction += math.pow(reduction, count)
                count += 1

    shape = MODIFIED_FACTORS['shape'][0]
    complication_multiplier = custom_values['complication_multipliers']['stroke multiplier']
    complication_prob = calculate_weibull_prob_t2d(shape, explanators, step, MODIFIED_FACTORS['intercept'][0],
                                                   complication_multiplier, total_risk_reduction)

    return rounder(complication_prob)


def modify_coefficients(data, rng):
    psa_factor = data
    global MODIFIED_FACTORS
    if psa_factor:
        modified_factors_dict = {}
        for factor, value in FACTORS.items():
            new_value = normal.model(rng, value[0], value[1], 4)
            modified_factors_dict[factor] = [new_value]
        MODIFIED_FACTORS = modified_factors_dict