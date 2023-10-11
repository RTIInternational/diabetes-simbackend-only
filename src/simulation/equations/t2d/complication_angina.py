from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "angina"

FACTORS = {
    "intercept": [-9.893, 0.677],
    "shape_accord": [-0.223, 0.059],
    "shape": [0.004, 0.045],
    "age_entry": [0.012, 0.005],
    "diabetes_duration_entry": [0.011, 0.004],
    "accord": [-0.087, 0.144],
    "twd_bmi": [0.022, 0.006],
    "twd_sbp": [0.004, 0.002],
    "twd_ldl": [0.006, 0.001],
    "twd_hdl": [-0.013, 0.004],
    "twd_hba1c": [0.142, 0.032],
    "twd_trig": [0.299, 0.073],
    "twd_serum_creatinine": [0.084, 0.123],
    "lagged_dialysis": [0.532, 0.197],
    "ever_revasc": [1.319, 0.077],
    "ever_mi": [0.494, 0.077],
    "ever_chf": [0.196, 0.112],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of angina
    """
    if has_event_in_simulation(individual, 'angina'):
        return 0

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['twd_bmi'][0] * time_weighted_risk_factor(individual, 'bmi')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_ldl'][0] * time_weighted_risk_factor(individual, 'ldl')
    explanators += MODIFIED_FACTORS['twd_hdl'][0] * time_weighted_risk_factor(individual, 'hdl')
    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')
    explanators += MODIFIED_FACTORS['twd_serum_creatinine'][0] * time_weighted_risk_factor(individual, 'serum_creatinine')

    if individual['accord'] == 1:
        explanators += MODIFIED_FACTORS['accord'][0]
        shape = MODIFIED_FACTORS['shape'][0] + MODIFIED_FACTORS['shape_accord'][0]
    else:
        shape = MODIFIED_FACTORS['shape'][0]

    if has_history(individual, 'dialysis', step):
        explanators += MODIFIED_FACTORS['lagged_dialysis'][0]

    if has_history(individual, 'revasc', step):
        explanators += MODIFIED_FACTORS['ever_revasc'][0]

    if has_history(individual, 'chf', step):
        explanators += MODIFIED_FACTORS['ever_chf'][0]

    if has_history(individual, 'mi', step):
        explanators += MODIFIED_FACTORS['ever_mi'][0]

    total_risk_reduction = 0
    if intervention and is_intervention:
        risk_reductions = intervention['risk reductions']
        count = 1
        # the relevant risk reductions were filtered out by the experiment manager
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

    complication_multiplier = custom_values['complication_multipliers']['angina multiplier']
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