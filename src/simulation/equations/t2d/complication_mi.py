from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "mi"

FACTORS = {
    "lambda_val": [-10.829, 0.588],
    "shape": [-0.025, 0.026],
    "age_entry": [0.033, 0.004],
    "diabetes_duration_entry": [0.014, 0.003],
    "has_postsecondary_ed": [-0.170, 0.060],
    "female": [-0.278, 0.064],
    "black": [-0.304, 0.086],
    "hispanic": [-0.244, 0.106],
    "curr_smoker": [0.252, 0.092],
    "twd_sbp": [0.010, 0.002],
    "twd_ldl": [0.008, 0.001],
    "twd_hdl": [-0.009, 0.003],
    "twd_hba1c": [0.156, 0.029],
    "twd_trig": [0.214, 0.066],
    "lagged_angina": [0.548, 0.095],
    "lagged_micro": [0.257, 0.061],
    "lagged_macro": [0.219, 0.078],
    "lagged_dialysis": [0.417, 0.162],
    "ever_revasc": [0.630, 0.066],
    "ever_stroke": [0.302, 0.086],
    "ever_mi": [0.388, 0.070],
    "ever_chf": [0.477, 0.092]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of myocardial infarction
    """

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['has_postsecondary_ed'][0] * individual['has_postsecondary_ed']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['black'][0] * individual['black']
    explanators += MODIFIED_FACTORS['hispanic'][0] * individual['hispanic']

    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_ldl'][0] * time_weighted_risk_factor(individual, 'ldl')
    explanators += MODIFIED_FACTORS['twd_hdl'][0] * time_weighted_risk_factor(individual, 'hdl')

    if get_event_in_step(individual, 'smoker', step):
        explanators += MODIFIED_FACTORS['curr_smoker'][0]

    if has_event_in_simulation(individual, 'angina'):
        explanators += MODIFIED_FACTORS['lagged_angina'][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_micro'][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_macro'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['mi multiplier']
    complication_prob = calculate_weibull_prob_t2d(shape, explanators, step, MODIFIED_FACTORS['lambda_val'][0],
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