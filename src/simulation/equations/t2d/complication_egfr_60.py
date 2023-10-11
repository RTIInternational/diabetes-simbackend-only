from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "egfr_60"

FACTORS = {
    "intercept": [-11.447, 0.310],
    "shape_accord": [-0.641, 0.029],
    "shape": [0.338, 0.026],
    "age_entry": [0.074, 0.002],
    "diabetes_duration_entry": [0.015, 0.002],
    "female": [0.157, 0.030],
    "black": [-0.144, 0.038],
    "hispanic": [-0.215, 0.051],
    "other_race": [-0.176, 0.046],
    "accord": [2.365, 0.092],
    "twd_bmi": [0.020, 0.002],
    "twd_sbp": [0.002, 0.001],
    "twd_hdl": [-0.006, 0.001],
    "twd_hba1c": [0.085, 0.015],
    "twd_trig": [0.189, 0.031],
    "lagged_angina": [0.110, 0.073],
    "lagged_micro": [0.230, 0.029],
    "lagged_macro": [0.544, 0.044],
    "ever_revasc": [0.193, 0.032],
    "ever_stroke": [0.145, 0.050],
    "ever_chf": [0.364, 0.055],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of eGFR < 60
    """
    if has_event(individual, 'egfr_60'):
        return 0

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['black'][0] * individual['black']
    explanators += MODIFIED_FACTORS['hispanic'][0] * individual['hispanic']
    explanators += MODIFIED_FACTORS['other_race'][0] * individual['other_race']
    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_hdl'][0] * time_weighted_risk_factor(individual, 'hdl')
    explanators += MODIFIED_FACTORS['twd_bmi'][0] * time_weighted_risk_factor(individual, 'bmi')

    if individual['accord'] == 1:
        explanators += MODIFIED_FACTORS['accord'][0]
        shape = MODIFIED_FACTORS['shape'][0] + MODIFIED_FACTORS['shape_accord'][0]
    else:
        shape = MODIFIED_FACTORS['shape'][0]

    if has_event_in_simulation(individual, 'angina'):
        explanators += MODIFIED_FACTORS['lagged_angina'][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_micro'][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_macro'][0]

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

    complication_multiplier = custom_values['complication_multipliers']['egfr_60 multiplier']
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