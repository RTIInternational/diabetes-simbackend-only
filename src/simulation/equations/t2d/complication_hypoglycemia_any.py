from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "hypoglycemia_any"

FACTORS = {
    "intercept": [-9.562, 0.454],
    "shape_accord": [-0.412, 0.068],
    "shape": [0.245, 0.063],
    "age_entry": [0.021, 0.004],
    "diabetes_duration_entry": [0.039, 0.003],
    "has_postsecondary_ed": [-0.287, 0.064],
    "female": [0.283, 0.058],
    "other_race": [-0.333, 0.100],
    "accord": [2.137, 0.203],
    "twd_bmi": [0.006, 0.005],
    "twd_hba1c": [0.146, 0.029],
    "twd_serum_creatinine": [0.787, 0.089],
    "lagged_micro": [0.157, 0.055],
    "ever_revasc": [0.126, 0.061],
    "ever_stroke": [0.202, 0.093],
    "ever_chf": [0.249, 0.105]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of hypoglycemia (any cause)
    """

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['has_postsecondary_ed'][0] * individual['has_postsecondary_ed']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['other_race'][0] * individual['other_race']
    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_bmi'][0] * time_weighted_risk_factor(individual, 'bmi')
    explanators += MODIFIED_FACTORS['twd_serum_creatinine'][0] * time_weighted_risk_factor(individual, 'serum_creatinine')

    if individual['accord'] == 1:
        # shape = np.exp(MODIFIED_FACTORS['shape'] + MODIFIED_FACTORS['shape_accord'][0])
        shape = MODIFIED_FACTORS['shape'][0] + MODIFIED_FACTORS['shape_accord'][0]
        explanators += MODIFIED_FACTORS['accord'][0]
    else:
        # shape = np.exp(MODIFIED_FACTORS['shape'][0])
        shape = MODIFIED_FACTORS['shape'][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_micro'][0]

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

    complication_multiplier = custom_values['complication_multipliers']['hypoglycemia_any multiplier']
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