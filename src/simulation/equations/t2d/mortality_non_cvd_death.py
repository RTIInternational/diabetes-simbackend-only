from src.simulation.utils import *
from src.simulation.equations.models import *
from copy import deepcopy

EVENT = "non_cvd_death"

FACTORS = {
    "intercept": [-11.943, 0.558],
    "shape": [0.090, 0.005],
    "female": [-0.203, 0.075],
    "hispanic": [-0.513, 0.144],
    "other": [-0.290, 0.128],
    "curr_smoker": [0.760, 0.115],
    "twd_bmi": [0.016, 0.006],
    "twd_hdl": [-0.008, 0.003],
    "twd_hba1c": [0.116, 0.038],
    "lag_tv_micro": [0.274, 0.070],
    "lag_tv_egfr_60": [0.204, 0.075],
    "lag_tv_egfr_30": [0.493, 0.158],
    "lag_tv_dialysis": [0.745, 0.193],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, *_):
    """
    Calculate probability of death
    """

    if has_event(individual, 'cvd'):
        return 0

    explanators = 0
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS["hispanic"][0] * individual['hispanic']
    explanators += MODIFIED_FACTORS["other"][0] * individual['other_race']
    explanators += MODIFIED_FACTORS["curr_smoker"][0] * get_event_in_step(individual, 'smoker', step)
    explanators += MODIFIED_FACTORS["twd_bmi"][0] * time_weighted_risk_factor(individual, 'bmi')
    explanators += MODIFIED_FACTORS["twd_hdl"][0] * time_weighted_risk_factor(individual, 'hdl')
    explanators += MODIFIED_FACTORS["twd_hba1c"][0] * time_weighted_risk_factor(individual, 'hba1c')

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS["lag_tv_micro"][0]

    if has_history(individual, 'egfr_30', step):
        explanators += MODIFIED_FACTORS["lag_tv_egfr_30"][0]

    if has_history(individual, 'egfr_60', step):
        explanators += MODIFIED_FACTORS["lag_tv_egfr_60"][0]

    if has_history(individual, 'dialysis', step):
        explanators += MODIFIED_FACTORS["lag_tv_dialysis"][0]

    current_age = individual['age']

    integrated_hazard_t = gompertz.model(explanators, current_age - 1, MODIFIED_FACTORS['intercept'][0], MODIFIED_FACTORS['shape'][0])
    integrated_hazard_t1 = gompertz.model(explanators, current_age, MODIFIED_FACTORS['intercept'][0], MODIFIED_FACTORS['shape'][0])

    mortality_multipliers = custom_values['mortality_multipliers']
    multiplier = mortality_multipliers['Equation 1']

    complication_prob = 1 - np.exp(multiplier * (integrated_hazard_t - integrated_hazard_t1))

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