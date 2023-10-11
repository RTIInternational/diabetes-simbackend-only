from src.simulation.utils import *

EVENT = "sbp"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 38.508960,
    "lag_value": 0.547247,
    "step": 1.218279,
    "initial_value": 0.118656,
    "female": 0.480256,
    "black": 1.503146,
    "hispanic": 0.325959,
    "age_entry": 0.037388,
    "diabetes_duration_entry": 0.011781,
    "has_postsecondary_ed": -0.384318,
    "la_trial": -1.795701,
    "intensive_la_treatment": -0.311611,
    "sbp_treatment": -3.297381
}


def calculate_default(individual, step):
    explanators = 0
    explanators += FACTORS["lag_value"] * get_event_in_step(individual, 'sbp', step - 1)
    explanators += FACTORS["step"] * math.log(step)
    explanators += FACTORS["initial_value"] * get_event_in_step(individual, 'sbp', 0)
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS['black'] * individual['black']
    explanators += FACTORS['hispanic'] * individual['hispanic']
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['la_trial'] * individual['la_trial']
    explanators += FACTORS['has_postsecondary_ed'] * individual['has_postsecondary_ed']
    explanators += FACTORS['intensive_la_treatment'] * individual['intensive_la_treatment']
    explanators += FACTORS['sbp_treatment'] * individual['sbp_treatment']

    return round(explanators + FACTORS['intercept'])


def target_mapping(type):
    mapping = {
        'individual["age"] >= 65': f'If age >= 65 {type}',
        'has_event(individual, "cvd")': f'If CVD = 1 {type}',
        'individual["age"] >= 65 and has_event(individual, "cvd")':
            f'If age >= 65 and CVD = 1 {type}'
    }
    return mapping


def calculate(individual, step, _, intervention, has_intervention):

    # user has chosen advanced intervention setup
    is_non_compliant = individual['bp_non_compliant']
    if intervention and intervention['bp_control_setup_type'] == 'advanced':
        modify_trajectory = intervention['bp_control_trajectory_advanced'][0]
        intensification = intervention['bp_control_intensification_advanced'][0]

        # all available target conditionals; these will be used in an eval expression below
        targets = [
            'individual["age"] >= 65',
            'has_event(individual, "cvd")',
            'individual["age"] >= 65 and has_event(individual, "cvd")'
        ]

        # targets with values specified by the user in the UI
        all_targets_dict = intervention["bp_control_targets_advanced"][0]

        # determine whether this is a non-intervention or intervention run
        run_type = 'Standard'
        if has_intervention and not is_non_compliant:
            run_type = 'Intervention'

        # get the number of drugs this individual has been on (default = 0)
        individual_drug = get_event_in_step(individual, 'bp drug', step - 1)
        # advanced intervention has a default value; this is the only way to distinguish the cost of the basic
        # intervention from the advanced on2
        if individual_drug == 0:
            individual_drug = 1

        # determine all targets that apply to this individual; if no conditional targets apply, use general one
        mapping = target_mapping(f'{run_type}')
        individual_target_dict = {}
        for target in targets:
            if eval(target):
                individual_target_dict[mapping[target]] = all_targets_dict[mapping[target]]
        if not individual_target_dict:
            target = all_targets_dict[f'General {run_type}']
        # determine max value and set that as the target value to use
        else:
            max_value = [max(individual_target_dict.values())][0]
            max_targets = [v for k, v in individual_target_dict.items() if v == max_value]
            target = max_targets[0]

        if not bool(modify_trajectory['custom_sbp_trajectory']):
            if step == 1:
                progression = calculate_default(individual, step)
            else:
                progression = get_event_in_step(individual, 'sbp', step - 1)
        # trajectory has been modified by user
        else:
            # if no drugs have been administered yet, apply sbp increase to baseline value
            if individual_drug == 1:
                effective_step = 0
                change = modify_trajectory[f'Annual SBP change Before {run_type}']
                # 1 is added to indicate default cost of advanced intervention
                individual['bp drug'].append(1)
            # apply to value from previous time step
            else:
                effective_step = step - 1
                # get the actual change value; dependent on type of run (non-intervention, intervention)
                change = modify_trajectory[f'Annual SBP change After {run_type}']
            # and calculate new sbp value
            progression = get_event_in_step(individual, 'sbp', effective_step) + change

        # drug labels are strings in the UI but is easier to just store the current drug as an additive number in an
        # individual; 1 = default so start with 2
        drug_mapping = {2: 'Effect of first drug on blood pressure ', 3: 'Effect of second drug on blood pressure ',
                        4: 'Effect of subsequent drug on blood pressure '}

        # if the new sbp value exceeds the determined target apply a drug
        if progression > target + all_targets_dict[f'Intensify if SBP > target {run_type}']:
            individual_drug += 1
            # only 3 drugs can be applied
            if individual_drug > 4:
                individual_drug = 4
            # get the reducing effect of the applicable drug
            drug_effect = intensification[drug_mapping[individual_drug] + run_type]
            # apply the effect of the drug ... negative entered value = improvement
            progression = progression + drug_effect
            # update individual with an additional drug
        individual['bp drug'].append(individual_drug)
    else:
        progression = calculate_default(individual, step)
        individual['bp drug'].append(get_event_in_step(individual, 'bp drug', step - 1))

    return rounder(progression)


def modify_coefficients(data, rng):
    pass