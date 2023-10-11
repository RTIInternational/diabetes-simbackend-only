from src.simulation.utils import *

EVENT = "health_cost"

IS_DETERMINISTIC = True


BEHAVIOR = 'APPEND'

def calculate(individual, step, economics, interventions, has_intervention):

    if individual['age'] > 65 and economics['include_medicare']:
        custom_costs = economics['costs_medicare']
    else:
        custom_costs = economics['costs']

    # time adjusted discount
    discount_factor = get_discount(custom_costs['cost discount factor'], step)

    age_cost = custom_costs['age cost']
    general_cost_component = custom_costs['base cost'] + individual['age'] * age_cost
    discounted_overall_cost = general_cost_component * discount_factor

    return rounder(discounted_overall_cost, 2)


def modify_coefficients(data, rng):
    pass