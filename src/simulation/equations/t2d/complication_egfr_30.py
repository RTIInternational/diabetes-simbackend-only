from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "egfr_30"

FACTORS = {
    "intercept": [-9.472, 0.799],
    "shape": [0.184, 0.033],
    "age_entry": [0.021, 0.006],
    "diabetes_duration_entry": [0.011, 0.005],
    "female": [0.574, 0.085],
    "accord": [0.284, 0.100],
    "twd_sbp": [0.014, 0.003],
    "twd_ldl": [0.003, 0.001],
    "twd_hdl": [-0.015, 0.005],
    "twd_trig": [0.249, 0.095],
    "lagged_micro": [0.450, 0.102],
    "lagged_macro": [1.100, 0.092],
    "ever_chf": [0.588, 0.112]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of eGFR < 30
    """
    if has_event(individual, 'egfr_30'):
        return 0

    # only execute if individual has microalbuminuria in a previous step
    if not has_history(individual, 'egfr_60', step):
        return 0

    # egfr30 calculations are based on the year of egfr60 diagnosis as opposed to
    # simulation start. We use the year of egfr60 diagnosis to update age at entry,
    # diabetes duration at entry and timestep.
    egfr60_diagnosis_step = get_time_of_event(individual, 'egfr_60')
    egfr30_step = step - egfr60_diagnosis_step

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * (individual['age_entry'] + egfr60_diagnosis_step)
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * (individual['diabetes_duration_entry'] + egfr60_diagnosis_step)
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['twd_hdl'][0] * time_weighted_risk_factor(individual, 'hdl')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_ldl'][0] * time_weighted_risk_factor(individual, 'ldl')

    if individual['accord'] == 1:
        explanators += MODIFIED_FACTORS['accord'][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_micro'][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS['lagged_macro'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['egfr_30 multiplier']
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