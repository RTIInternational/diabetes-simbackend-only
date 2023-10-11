from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "microalbuminuria"

FACTORS = {
    "intercept": [-12.078, 0.421],
    "shape": [0.238, 0.015],
    "age_entry": [0.029, 0.003],
    "has_postsecondary_ed": [-0.103, 0.037],
    "hispanic": [-0.118, 0.064],
    "other_race": [0.123, 0.057],
    "curr_smoker": [0.306, 0.066],
    "twd_bmi": [0.019, 0.003],
    "twd_sbp": [0.018, 0.001],
    "twd_hdl": [-0.006, 0.002],
    "twd_hba1c": [0.323, 0.018],
    "twd_trig": [0.236, 0.042],
    "twd_serum_creatinine": [0.556, 0.101],
    "lagged_egfr_60": [0.139, 0.049],
    "ever_revasc": [0.171, 0.042],
    "ever_stroke": [0.122, 0.073],
    "ever_chf": [0.345, 0.085]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of microalbuminuria
    """
    if has_event(individual, 'microalbuminuria'):
        return 0
    
    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['has_postsecondary_ed'][0] * individual['has_postsecondary_ed']
    explanators += MODIFIED_FACTORS['hispanic'][0] * individual['hispanic']
    explanators += MODIFIED_FACTORS['other_race'][0] * individual['other_race']
    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_hdl'][0] * time_weighted_risk_factor(individual, 'hdl')
    explanators += MODIFIED_FACTORS['twd_bmi'][0] * time_weighted_risk_factor(individual, 'bmi')
    explanators += MODIFIED_FACTORS['twd_serum_creatinine'][0] * time_weighted_risk_factor(individual, 'serum_creatinine')

    if get_event_in_step(individual, 'smoker', step):
        explanators += MODIFIED_FACTORS['curr_smoker'][0]

    if has_history(individual, 'egfr_60', step):
        explanators += MODIFIED_FACTORS['lagged_egfr_60'][0]

    if has_history(individual, 'revasc', step):
        explanators += MODIFIED_FACTORS['ever_revasc'][0]

    if has_history(individual, 'stroke', step):
        explanators += MODIFIED_FACTORS['ever_stroke'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['microalbuminuria multiplier']
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