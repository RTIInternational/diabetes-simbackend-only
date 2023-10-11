from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "revasc"

FACTORS = {
    "intercept": [-9.849, 0.436],
    "shape": [0.021, 0.019],
    "age_entry": [0.025, 0.003],
    "diabetes_duration_entry": [0.015, 0.003],
    "has_postsecondary_ed": [-0.052, 0.045],
    "female": [-0.523, 0.051],
    "black": [-0.356, 0.067],
    "hispanic": [-0.419, 0.089],
    "other_race": [-0.271, 0.071],
    "curr_smoker": [0.285, 0.069],
    "twd_sbp": [0.010, 0.002],
    "twd_ldl": [0.006, 0.001],
    "twd_hdl": [-0.009, 0.003],
    "twd_hba1c": [0.153, 0.022],
    "twd_trig": [0.275, 0.050],
    "lagged_angina": [0.599, 0.146],
    "ever_revasc": [0.659, 0.050],
    "ever_stroke": [0.224, 0.069],
    "ever_mi": [0.360, 0.056],
    "prior_step_mi": [2.427, 0.077],
    "prior_step_angina": [2.956, 0.077]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of revascularization
    """

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['has_postsecondary_ed'][0] * individual['has_postsecondary_ed']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['black'][0] * individual['black']
    explanators += MODIFIED_FACTORS['hispanic'][0] * individual['hispanic']
    explanators += MODIFIED_FACTORS['other_race'][0] * individual['other_race']
    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_ldl'][0] * time_weighted_risk_factor(individual, 'ldl')
    explanators += MODIFIED_FACTORS['twd_hdl'][0] * time_weighted_risk_factor(individual, 'hdl')

    if get_event_in_step(individual, 'smoker', step):
        explanators += MODIFIED_FACTORS['curr_smoker'][0]

    if has_event_in_simulation(individual, 'angina'):
        explanators += MODIFIED_FACTORS['lagged_angina'][0]

    if has_history(individual, 'revasc', step):
        explanators += MODIFIED_FACTORS['ever_revasc'][0]

    if has_history(individual, 'stroke', step):
        explanators += MODIFIED_FACTORS['ever_stroke'][0]

    if has_history(individual, 'mi', step):
        explanators += MODIFIED_FACTORS['ever_mi'][0]

    if has_acute_event_in_simulation(individual, 'mi', step):
        explanators += MODIFIED_FACTORS['prior_step_mi'][0]

    if has_acute_event_in_simulation(individual, 'angina', step):
        explanators += MODIFIED_FACTORS['prior_step_angina'][0]

    total_risk_reduction = 0
    if intervention and is_intervention:
        # only basic interventions have risk reductions
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
    complication_multiplier = custom_values['complication_multipliers']['revasc multiplier']
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