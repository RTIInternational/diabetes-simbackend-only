from src.simulation.utils import *

EVENT = "ldl"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 30.596480,
    "lag_value": 0.632202,
    "step": -1.659944,
    "initial_value": 0.075947,
    "female": 2.714128,
    "black": 3.540492,
    "hispanic": 1.511537,
    "age_entry": -0.074629,
    "diabetes_duration_entry": -0.066090,
    "has_postsecondary_ed": -0.532848,
    "la_trial": -0.578092,
    "intensive_la_treatment": 0.636137,
    "ldl_treatment": -1.746743
}


def calculate_default(individual, step):
    explanators = 0
    explanators += FACTORS["lag_value"] * get_event_in_step(individual, 'ldl', step - 1)
    explanators += FACTORS["step"] * math.log(step)
    explanators += FACTORS["initial_value"] * get_event_in_step(individual, 'ldl', 0)
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS['black'] * individual['black']
    explanators += FACTORS['hispanic'] * individual['hispanic']
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['la_trial'] * individual['la_trial']
    explanators += FACTORS['has_postsecondary_ed'] * individual['has_postsecondary_ed']
    explanators += FACTORS['intensive_la_treatment'] * individual['intensive_la_treatment']
    explanators += FACTORS['ldl_treatment'] * individual['ldl_treatment']

    return explanators + FACTORS['intercept']


def calculate(individual, step, _, intervention, has_intervention):

    # if "modify trajectory" selected don't do this but use the provided value
    progression = calculate_default(individual, step)

    # check if advanced intervention applies
    is_non_compliant = individual['cholesterol_non_compliant']
    if intervention and intervention['cholesterol_control_setup_type'] == 'advanced':
        ldl_reductions = intervention['cholesterol_control_advanced'][0]
        statin_reductions = intervention['cholesterol_control_statin'][0]
        # determine whether this is a non-intervention or intervention run
        age_type = 'Standard'
        if has_intervention and not is_non_compliant:
            age_type = 'Intervention'
        min_age = ldl_reductions[f'Treatment begins at age {age_type}']

        # a user specified trajectory is applied to both, non-intervention and intervention runs
        # min age for treatment depends on the type of run
        trajectory_info = intervention['cholesterol_control_trajectory'][0]
        if trajectory_info['modify_trajectory'] == 'modify_trajectory' and individual['age'] < min_age:
            ldl_change = trajectory_info['annual_ldl_change']
            progression = get_event_in_step(individual, 'ldl', step - 1) + ldl_change

        # only apply if individual is at least as old as user specified minimum age
        # per instruction, intervention and non-intervention values are the same
        if individual['age'] >= min_age:
            run_type = 'std'
            if has_intervention:
                run_type = 'int'
            cvd_type = 0
            if has_event(individual, 'cvd'):
                cvd_type = 1
            if ldl_reductions[f'moderate_statin_cvd{cvd_type}_{run_type}'] == 1:
                statin_reduction = statin_reductions['moderate_statin_reduction']
                statin_type = 1
            elif ldl_reductions[f'high_statin_cvd{cvd_type}_{run_type}'] == 1:
                statin_reduction = statin_reductions['high_statin_reduction']
                statin_type = 2
            else:
                statin_reduction = 0
                statin_type = 0

            progression = progression * (1 - statin_reduction)
            individual['statin type'].append(statin_type)
        else:
            individual['statin type'].append(0)

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass