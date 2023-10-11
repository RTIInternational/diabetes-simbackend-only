from src.simulation.utils import *

EVENT = "intervention_cost"

IS_DETERMINISTIC = True

BEHAVIOR = 'APPEND'

# 1 indicates no drug
DRUGS = {1: 'default ', 2: 'drug 1 ', 3: 'drug 2 ', 4: 'drug 3 '}


def calculate(individual, step, economics, interventions, has_intervention):

    if individual['age'] > 65 and economics['include_medicare']:
        custom_costs = economics['costs_medicare']
    else:
        custom_costs = economics['costs']

    # time adjusted discount
    discount_factor = get_discount(custom_costs['cost discount factor'], step)

    intervention_cost_component = 0
    # applies costs of advanced interventions; this also includes non_intervention runs where disease trajectories
    # have been changed
    if interventions:
        all_intervention_costs = economics['intervention costs']
        suffix = 'control_intervention'
        # indicates actual intervention runs
        if has_intervention:
            # basic cost only applies to basic interventions
            for intervention in ['generic', 'glycemic', 'cholesterol', 'bp']:
                actual_cost = 0
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
                        if individual['age'] >= chol_intervention['age']:
                            actual_cost = individual[intervention_type] * intervention_cost
                    else:
                        actual_cost = individual[intervention_type] * intervention_cost
                if 'smoking' in all_intervention_costs.keys():
                    intervention_cost = all_intervention_costs['smoking']
                    actual_cost = get_event_in_step(individual, 'quit_smoking', step) * intervention_cost
                intervention_cost_component += actual_cost


        # advanced glycemic and blood pressure intervention
        for target in ['glycemic', 'bp']:
            if target in all_intervention_costs:
                if has_intervention:
                    run_type = 'intervention'
                else:
                    run_type = 'standard'
                intervention_cost = all_intervention_costs[target]
                drug_type = get_event_in_step(individual, f'{target} drug', step)
                # 0 indicates no intervention was applied
                if drug_type > 0:
                    drug_cost = intervention_cost[DRUGS[drug_type] + run_type]
                    intervention_cost_component += drug_cost

        # advanced cholesterol intervention
        statin_type = get_event_in_step(individual, 'statin type', step)
        if statin_type == 1:
            ldl_drug_cost = all_intervention_costs['statin type']['1']
        elif statin_type == 2:
            ldl_drug_cost = all_intervention_costs['statin type']['2']
        else:
            ldl_drug_cost = 0
        intervention_cost_component += ldl_drug_cost

    discounted_overall_cost = intervention_cost_component * discount_factor

    return rounder(discounted_overall_cost, 2)


def modify_coefficients(data, rng):
    pass