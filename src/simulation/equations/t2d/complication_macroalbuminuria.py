from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "macroalbuminuria"

FACTORS = {
    "intercept": [-12.829, 0.455],
    "shape_accord": [0.272, 0.048],
    "shape": [0.265, 0.048],
    "hispanic": [0.187, 0.091],
    "other_race": [0.200, 0.078],
    "accord": [-0.694, 0.150],
    "curr_smoker": [0.357, 0.092],
    "twd_sbp": [0.033, 0.002],
    "twd_hba1c": [0.257, 0.027],
    "twd_trig": [0.300, 0.053],
    "twd_serum_creatinine": [0.900, 0.114],
    "lagged_egfr_60": [0.351, 0.070],
    "ever_revasc": [0.203, 0.057],
    "ever_chf": [0.204, 0.106],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention):
    """
    Calculate probability of macroalbuminuria
    """
    if has_event(individual, 'macroalbuminuria'):
        return 0

    # only execute if individual has microalbuminuria in a previous step
    if not has_history(individual, 'microalbuminuria', step):
        return 0

    # Macro calculations are based on the year of micro diagnosis as opposed to
    # simulation start. We use the year of micr diagnosis to update age at entry,
    # diabetes duration at entry and timestep.
    micro_diagnosis_step = get_time_of_event(individual, 'microalbuminuria')
    macro_step = step - micro_diagnosis_step

    explanators = 0
    explanators += MODIFIED_FACTORS['hispanic'][0] * individual['hispanic']
    explanators += MODIFIED_FACTORS['other_race'][0] * individual['other_race']
    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_serum_creatinine'][0] * time_weighted_risk_factor(individual, 'serum_creatinine')

    if individual['accord'] == 1:
        explanators += MODIFIED_FACTORS['accord'][0]
        shape = MODIFIED_FACTORS['shape'][0] + MODIFIED_FACTORS['shape_accord'][0]
    else:
        shape = MODIFIED_FACTORS['shape'][0]

    if get_event_in_step(individual, 'smoker', step):
        explanators += MODIFIED_FACTORS['curr_smoker'][0]

    if has_history(individual, 'egfr_60', step):
        explanators += MODIFIED_FACTORS['lagged_egfr_60'][0]

    if has_history(individual, 'revasc', step):
        explanators += MODIFIED_FACTORS['ever_revasc'][0]

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

    complication_multiplier = custom_values['complication_multipliers']['macroalbuminuria multiplier']
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