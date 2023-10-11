from src.simulation.utils import *

EVENT = "qaly"

IS_DETERMINISTIC = True

BEHAVIOR = 'APPEND'

EVENTS = ["stroke", "amputation", "dialysis", "mi", "chf", "angina", "egfr_60", "egfr_30", "revasc",
          "laser_retina", "blindness", "ulcer", "neurop", "hypoglycemia_medical", "hypoglycemia_any"]
DEMOGRAPHIC_EVENTS = ["smoker", "bmi"]


def calculate(individual, step, economics, *_):

    custom_disutilities = economics['disutilities']

    discount_value = custom_disutilities['qaly discount factor']
    discount_factor = get_discount(discount_value, step)

    # constant term in variable Excel sheet
    qaly = custom_disutilities['base qaly']

    for event in EVENTS:
        if has_event_in_step(individual, event, step):
            qaly += custom_disutilities[event][0]
        if has_history_in_simulation(individual, event, step):
            qaly += custom_disutilities[event][1]

    for event in DEMOGRAPHIC_EVENTS:
        qaly += custom_disutilities[event][0] * get_event_in_step(individual, event, step)

    # per health economics expert:
    # For duration, we actually need time-varying duration. For each year that passes in the simulation,
    # their duration variable should increase by 1
    qaly += custom_disutilities['diabetes_duration_entry'][0] * (individual['diabetes_duration_entry'] + step)

    discounted_qaly = qaly * discount_factor

    return rounder(discounted_qaly, 4)


def modify_coefficients(data, rng):
    pass