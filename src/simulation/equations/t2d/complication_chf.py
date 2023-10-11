from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "chf"

FACTORS = {
    "intercept": [-15.396, 0.632],
    "shape": [0.604, 0.032],
    "age_entry": [0.063, 0.005],
    "diabetes_duration_entry": [0.009, 0.004],
    "has_postsecondary_ed": [-0.229, 0.074],
    "black": [0.238, 0.091],
    "hispanic": [-0.244, 0.140],
    "other_race": [-0.239, 0.130],
    "curr_smoker": [0.273, 0.126],
    "twd_bmi": [0.052, 0.006],
    "twd_sbp": [0.007, 0.003],
    "twd_hdl": [-0.020, 0.003],
    "twd_hba1c": [0.218, 0.035],
    "lagged_angina": [0.406, 0.095],
    "lagged_micro": [0.465, 0.080],
    "lagged_macro": [0.543, 0.082],
    "lagged_egfr_60": [0.292, 0.074],
    "lagged_egfr_30": [0.312, 0.109],
    "lagged_dialysis": [0.470, 0.146],
    "ever_revasc": [0.757, 0.080],
    "ever_mi": [0.785, 0.075]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of congestive heart failure
    """
    if has_event_in_simulation(individual, 'chf'):
        return 0

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['has_postsecondary_ed'][0] * individual['has_postsecondary_ed']
    explanators += MODIFIED_FACTORS['black'][0] * individual['black']
    explanators += MODIFIED_FACTORS['hispanic'][0] * individual['hispanic']
    explanators += MODIFIED_FACTORS['other_race'][0] * individual['other_race']

    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_bmi'][0] * time_weighted_risk_factor(individual, 'bmi')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_hdl'][0] * time_weighted_risk_factor(individual, 'hdl')

    if get_event_in_step(individual, 'smoker', step):
        explanators += MODIFIED_FACTORS['curr_smoker'][0]

    # We don’t have a baseline value for angina history for both input data sets so we can’t use baseline for angina.
    if has_event_in_simulation(individual, 'angina'):
        explanators += MODIFIED_FACTORS['lagged_angina'][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_micro'][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_macro'][0]

    if has_history(individual, 'egfr_60', step):
        explanators += MODIFIED_FACTORS['lagged_egfr_60'][0]

    if has_history(individual, 'egfr_30', step):
        explanators += MODIFIED_FACTORS['lagged_egfr_30'][0]

    if has_history(individual, 'dialysis', step):
        explanators += MODIFIED_FACTORS['lagged_dialysis'][0]

    if has_history(individual, 'revasc', step):
        explanators += MODIFIED_FACTORS['ever_revasc'][0]

    if has_history(individual, 'mi', step):
        explanators += MODIFIED_FACTORS['ever_mi'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['chf multiplier']
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