from src.simulation.utils import *
from src.simulation.equations.models import *
from copy import deepcopy

EVENT = "ever_cvd_death"

FACTORS = {
    "intercept": [-11.317, 0.782],
    "shape": [0.078, 0.005],
    "female": [-0.276, 0.090],
    "black": [0.221, 0.110],
    "other": [-0.521, 0.168],
    "curr_smoker": [0.797, 0.110],
    "twd_sbp": [-0.007, 0.003],
    "twd_hba1c": [0.189, 0.044],
    "twd_trig": [0.145, 0.085],
    "lag_tv_micro": [0.456, 0.089],
    "lag_tv_macro": [0.184, 0.100],
    "lag_tv_egfr_30": [0.428, 0.132],
    "lag_tv_dialysis": [0.668, 0.171],
    "ever_stroke": [0.341, 0.089],
    "ever_mi": [0.221, 0.089],
    "ever_chf": [0.569, 0.087]
}
MODIFIED_FACTORS = deepcopy(FACTORS)

def calculate(individual, step, custom_values, *_):
    """
    Calculate probability of death for individuals who've had a cvd event prior to this step
    """

    # make sure the individual has had any of the qualifying events in the past but not during the current time step
    if(has_event_in_step(individual, 'cvd', step) or not has_history(individual, 'cvd', step)):
        return 0

    explanators = 0
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['black'][0] * individual['black']
    explanators += MODIFIED_FACTORS['other'][0] * individual['other_race']
    explanators += MODIFIED_FACTORS["curr_smoker"][0] * get_event_in_step(individual, 'smoker', step)
    explanators += MODIFIED_FACTORS['twd_sbp'][0] * time_weighted_risk_factor(individual, 'sbp')
    explanators += MODIFIED_FACTORS['twd_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['twd_trig'][0] * time_weighted_risk_factor(individual, 'trig')

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS["lag_tv_macro"][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS["lag_tv_micro"][0]

    if has_history(individual, 'egfr_30', step):
        explanators += MODIFIED_FACTORS["lag_tv_egfr_30"][0]

    if has_history(individual, 'dialysis', step):
        explanators += MODIFIED_FACTORS["lag_tv_dialysis"][0]

    if has_history(individual, 'stroke', step):
        explanators += MODIFIED_FACTORS['ever_stroke'][0]

    if has_history(individual, 'mi', step):
        explanators += MODIFIED_FACTORS['ever_mi'][0]

    if has_history(individual, 'chf', step):
        explanators += MODIFIED_FACTORS['ever_chf'][0]

    current_age = individual['age']

    integrated_hazard_t = gompertz.model(explanators, current_age - 1, MODIFIED_FACTORS['intercept'][0], MODIFIED_FACTORS['shape'][0])
    integrated_hazard_t1 = gompertz.model(explanators, current_age, MODIFIED_FACTORS['intercept'][0], MODIFIED_FACTORS['shape'][0])

    mortality_multipliers = custom_values['mortality_multipliers']
    multiplier = mortality_multipliers['Equation 3']

    complication_prob = 1 - np.exp(multiplier * (integrated_hazard_t - integrated_hazard_t1))

    return rounder(complication_prob)


def modify_coefficients(data, rng):
    psa_factor = data
    global MODIFIED_FACTORS
    if psa_factor :
        modified_factors_dict = {}
        for factor, value in FACTORS.items():
            new_value = normal.model(rng, value[0], value[1], 4)
            modified_factors_dict[factor] = [new_value]
        MODIFIED_FACTORS = modified_factors_dict
