from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "hypoglycemia_medical"

FACTORS = {
    "intercept": [-8.180, 0.393],
    "shape": [-0.033, 0.026],
    "age_entry": [0.026, 0.004],
    "diabetes_duration_entry": [0.028, 0.003],
    "has_postsecondary_ed": [-0.119, 0.065],
    "female": [0.264, 0.060],
    "black": [0.223, 0.069],
    "hispanic": [0.277, 0.100],
    "other_race": [-0.267, 0.101],
    "twd_hba1c": [0.165, 0.033],
    "twd_serum_creatinine": [0.665, 0.086],
    "lagged_angina": [0.237, 0.127],
    "lagged_micro": [0.158, 0.061],
    "lagged_macro": [0.166, 0.084],
    "ever_revasc": [0.206, 0.063],
    "ever_stroke": [0.342, 0.084],
    "ever_chf": [0.266, 0.105],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of hypoglycemia (medically induced)
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
    explanators += MODIFIED_FACTORS['twd_serum_creatinine'][0] * time_weighted_risk_factor(individual, 'serum_creatinine')

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

    shape = MODIFIED_FACTORS['shape'][0]
    complication_multiplier = custom_values['complication_multipliers']['hypoglycemia_medical multiplier']
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