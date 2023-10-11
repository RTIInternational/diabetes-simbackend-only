from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "laser_retina"

FACTORS = {
    "intercept": [-9.080, 0.336],
    "shape_accord": [-0.188, 0.048],
    "shape": [0.062, 0.038],
    "diabetes_duration_entry": [0.051, 0.003],
    "female": [0.197, 0.057],
    "other_race": [-0.186, 0.089],
    "accord": [0.077, 0.125],
    "twd_sbp": [0.013, 0.002],
    "twd_ldl": [0.003, 0.001],
    "twd_hba1c": [0.204, 0.025],
    "twd_serum_creatinine": [0.551, 0.100],
    "lagged_micro": [0.266, 0.059],
    "lagged_macro": [0.248, 0.081],
    "ever_stroke": [0.176, 0.095],
    "ever_chf": [0.310, 0.110],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of laser retinopathy
    """
    if has_event_in_simulation(individual, 'laser_retina'):
        return 0

    explanators = 0
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['other_race'][0] * individual['other_race']
    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_ldl'][0] * time_weighted_risk_factor(individual, 'ldl')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_serum_creatinine'][0] * time_weighted_risk_factor(individual, 'serum_creatinine')

    if individual['accord'] == 1:
        explanators += MODIFIED_FACTORS['accord'][0]
        shape = MODIFIED_FACTORS['shape'][0] + MODIFIED_FACTORS['shape_accord'][0]
    else:
        shape = MODIFIED_FACTORS['shape'][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_micro'][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_macro'][0]

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

    complication_multiplier = custom_values['complication_multipliers']['laser_retina multiplier']
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