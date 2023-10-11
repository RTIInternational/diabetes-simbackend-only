from src.simulation.utils import *

EVENT = "trig"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 1.079021,
    "lag_value": 0.670164,
    "step": -0.019114,
    "initial_value": 0.140038,
    "female": 0.004601,
    "black": -0.054986,
    "hispanic": 0.003588,
    "age_entry": -0.001690,
    "diabetes_duration_entry": -0.000907,
    "has_postsecondary_ed": -0.014083,
    "la_trial": -0.033190,
    "intensive_la_treatment": 0.007600,
    "trig_treatment": -0.027222
}


def calculate_default(individual, step):

    explanators = 0
    explanators += FACTORS["lag_value"] * get_event_in_step(individual, 'trig', step - 1)
    explanators += FACTORS["step"] * math.log(step)
    explanators += FACTORS["initial_value"] * get_event_in_step(individual, 'trig', 0)
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS['black'] * individual['black']
    explanators += FACTORS['hispanic'] * individual['hispanic']
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['la_trial'] * individual['la_trial']
    explanators += FACTORS['has_postsecondary_ed'] * individual['has_postsecondary_ed']
    explanators += FACTORS['intensive_la_treatment'] * individual['intensive_la_treatment']
    explanators += FACTORS['trig_treatment'] * individual['trig_treatment']

    return explanators + FACTORS['intercept']


def calculate(individual, step, _, intervention, has_intervention):
    if intervention and intervention['cholesterol_control_setup_type'] == 'advanced':
        trig_reductions = intervention['cholesterol_control_advanced'][0]
        is_non_compliant = individual['cholesterol_non_compliant']
        age_type = 'Standard'
        if has_intervention and not is_non_compliant:
            age_type = 'Intervention'
        min_age = trig_reductions[f'Treatment begins at age {age_type}']
        # a user specified trajectory is applied to both, non-intervention and intervention runs
        # min age for treatment depends on the type of run
        trajectory_info = intervention['cholesterol_control_trajectory'][0]
        if trajectory_info['modify_trajectory'] == 'modify_trajectory' and individual['age'] < min_age:
            trig_change = trajectory_info['annual_triglycerides_change']
            progression = get_event_in_step(individual, 'trig', step - 1) + trig_change
        else:
            progression = calculate_default(individual, step)
    else:
        progression = calculate_default(individual, step)

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass