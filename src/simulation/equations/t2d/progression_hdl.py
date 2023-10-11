from src.simulation.utils import *

EVENT = "hdl"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 1.690647,
    "lag_value": 0.748451,
    "step": 0.289586,
    "initial_value": 0.185481,
    "female": 0.675107,
    "black": 0.392465,
    "hispanic": 0.090015,
    "age_entry": 0.011317,
    "diabetes_duration_entry": -0.007298,
    "has_postsecondary_ed": 0.167871,
    "la_trial": 0.560408,
    "intensive_la_treatment": 0.183393,
    "hdl_treatment": -0.009843
}


def calculate_default(individual, step):
    explanators = 0
    explanators += FACTORS["lag_value"] * get_event_in_step(individual, 'hdl', step - 1)
    explanators += FACTORS["step"] * math.log(step)
    explanators += FACTORS["initial_value"] * get_event_in_step(individual, 'hdl', 0)
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS['black'] * individual['black']
    explanators += FACTORS['hispanic'] * individual['hispanic']
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['la_trial'] * individual['la_trial']
    explanators += FACTORS['has_postsecondary_ed'] * individual['has_postsecondary_ed']
    explanators += FACTORS['intensive_la_treatment'] * individual['intensive_la_treatment']
    explanators += FACTORS['hdl_treatment'] * individual['hdl_treatment']

    return explanators + FACTORS['intercept']


def calculate(individual, step, _, intervention, has_intervention):
    if intervention and intervention['cholesterol_control_setup_type'] == 'advanced':
        hdl_reductions = intervention['cholesterol_control_advanced'][0]
        is_non_compliant = individual['cholesterol_non_compliant']
        age_type = 'Standard'
        if has_intervention and not is_non_compliant:
            age_type = 'Intervention'
        min_age = hdl_reductions[f'Treatment begins at age {age_type}']
        # a user specified trajectory is applied to both, non-intervention and intervention runs
        # min age for treatment depends on the type of run
        trajectory_info = intervention['cholesterol_control_trajectory'][0]
        if trajectory_info['modify_trajectory'] == 'modify_trajectory' and individual['age'] < min_age:
            hdl_change = trajectory_info['annual_hdl_change']
            progression = get_event_in_step(individual, 'hdl', step - 1) + hdl_change
        else:
            progression = calculate_default(individual, step)
    else:
        progression = calculate_default(individual, step)

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass