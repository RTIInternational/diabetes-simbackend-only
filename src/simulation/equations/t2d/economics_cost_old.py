from src.simulation.utils import *

EVENT = "health_cost"

IS_DETERMINISTIC = True

BEHAVIOR = 'APPEND'

EVENTS = ["microalbuminuria", "macroalbuminuria", "stroke", "amputation", "dialysis", "mi", "chf", "angina",
          "egfr_60", "egfr_30", "revasc", "laser_retina", "blindness", "ulcer", "neurop", "hypoglycemia_any",
          "hypoglycemia_medical"]

DRUGS = {1: 'default ', 2: 'drug 1 ', 3: 'drug 2 ', 4: 'drug 3 '}


def calculate(individual, step, economics, interventions, has_intervention):

    if individual['age'] > 65 and economics['include_medicare']:
        custom_costs = economics['costs_medicare']
    else:
        custom_costs = economics['costs']

    # time adjusted discount
    discount_factor = get_discount(custom_costs['cost discount factor'], step)

    age_cost = custom_costs['age cost']

    general_cost_component = custom_costs['base cost'] + individual['age'] * age_cost

    event_cost_component = 0
    for event in EVENTS:
        if has_event_in_step(individual, event, step):
            event_cost_component += custom_costs[event][0]
        if has_history_in_simulation(individual, event, step):
            event_cost_component += custom_costs[event][1]

    if has_event_in_step(individual, 'death', step):
        event_cost_component = custom_costs['death_cost']

    intervention_cost_component = 0
    # applies costs of advanced interventions; this also includes non_intervention runs where disease trajectories
    # have been changed
    if interventions:
        all_intervention_costs = economics['intervention costs']
        run_type = 'standard'
        suffix = 'control_intervention'
        # indicates actual intervention runs
        if has_intervention:
            # run_type = 'intervention'
            # basic cost only applies to basic interventions
            actual_cost = 0
            for intervention in ['generic', 'glycemic', 'cholesterol', 'bp', 'smoking']:
                if f'baseline {intervention} intervention' in all_intervention_costs.keys():
                    intervention_type = f'baseline {intervention} intervention'
                    intervention_cost = all_intervention_costs[intervention_type]
                    if intervention == 'bp':
                        bp_intervention = interventions[f'{intervention}_{suffix}'][f'{intervention}_{suffix}'][0]
                        # note: That is, whether you get the intervention and incur its costs only depends
                        # on the baseline SBP (per Thomas Hoerger)
                        if get_event_in_step(individual, 'sbp', 0) > bp_intervention['apply if greater than']:
                            actual_cost = individual[intervention_type] * intervention_cost
                    elif intervention == 'cholesterol':
                        chol_intervention = interventions[f'{intervention}_{suffix}'][f'{intervention}_{suffix}'][0]
                        if individual['age'] < chol_intervention['age']:
                            actual_cost = individual[intervention_type] * intervention_cost
                    elif intervention == 'smoking':
                        actual_cost = get_event_in_step(individual, 'quit_smoking', step) * intervention_cost
                    else:
                        actual_cost = individual[intervention_type] * intervention_cost
                    intervention_cost_component += actual_cost

        for target in ['glycemic', 'bp']:
            if target in all_intervention_costs:
                intervention_cost = all_intervention_costs[target]
                drug_type = get_event_in_step(individual, f'{target} drug', step)
                # 0 indicates no intervention was applied
                if drug_type > 0:
                    drug_cost = intervention_cost[DRUGS[drug_type] + run_type]
                    intervention_cost_component += drug_cost

        statin_type = get_event_in_step(individual, 'statin type', step)
        if statin_type == 1:
            ldl_drug_cost = all_intervention_costs['statin type']['1']
        elif statin_type == 2:
            ldl_drug_cost = all_intervention_costs['statin type']['2']
        else:
            ldl_drug_cost = 0
        intervention_cost_component += ldl_drug_cost

    overall_cost = general_cost_component + event_cost_component + intervention_cost_component

    discounted_overall_cost = overall_cost * discount_factor

    return rounder(discounted_overall_cost, 2)
