from random import uniform
import math
from numba import jit
from src.simulation.equations.models import weibull, gompertz
import numpy as np

def rounder(number, ndigits=4):
    """
    Round a float to a specified length. This abstraction ensures values are in
    the correct data type

    :param number: number to round
    :param ndigits: number of digits to round to (default 4)
    :return: float rounded to ndigits
    """
    try:
        return round(float(number), ndigits)
    except (ValueError, TypeError):
        # Convert strings or None to 0
        return 0


def generate_random_probability():
    """
    Generate a random probability comparison

    :returns: "random" probability
    """
    return rounder(uniform(0, 1))


def get_value(key, dictionary, fallback):
    """
    Get the the value of a key from a dictionary. If the key is not available,
    fallback to a default dictionary. This assumes key is valid.

    :param key: factor key
    :param dictionary: dictionary to check
    :param fallback: fallback dictionary
    :return: value associated with key
    """
    if key in dictionary:
        return dictionary[key]
    else:
        return fallback[key]


def get_discount(rate, time):
    return rounder(1 / ((1 + rate) ** time), 2)


def has_event(individual, flag):
    """
    Determine whether an individual has ever had an event - including the current step

    :param individual: member of the population
    :param flag: key to evaluate
    :return: has there been an event?
    """
    return any(individual[flag])


def has_event_in_step(individual, flag, step):
    """
    Determine whether or not an individual has had an event in a given step - including the current step

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: has there been an event?
    """
    return bool(get_event_in_step(individual, flag, step, default=False))


def has_acute_event(individual, flag, step):
    """
    Determine whether or not an individual has an event in the step immediately prior

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: has there been an event?
    """
    return has_event_in_step(individual, flag, step - 1)


def has_acute_event_in_simulation(individual, flag, step):
    """
    Determine whether or not an individual has an event in the step immediately prior

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: has there been an event?
    """
    if step > 1:
        return has_event_in_step(individual, flag, step - 1)
    return 0


def has_history(individual, flag, step):
    """
    Determine whether an individual has had an event prior to the current
    step

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: is any flag truthy?
    """
    return any(individual[flag][:step])


def has_history_in_simulation(individual, flag, step):
    """
    Determine whether or not an individual has had an event during the simulation but prior to the current step.

    Certain T2D equations look for diagnosis of a complication during the
    simulation only, ignoring any events at baseline.

    :param individual: member of the population
    :param flag: key to evaluate
    :return: has there been an event?
    """
    return any(individual[flag][1:step])


def has_event_in_simulation(individual, flag):
    """
    Determine whether or not an individual has had an event during the simulation.

    Certain T2D equations look for diagnosis of a complication during the
    simulation only, ignoring any events at baseline.

    :param individual: member of the population
    :param flag: key to evaluate
    :return: has there been an event?
    """
    return any(individual[flag][1:])


def get_event(individual, flag):
    """
    Get the individuals history for an event

    :param individual: member of the population
    :param flag: key to evaluate
    :return: event list
    """
    return individual[flag]


def get_event_in_step(individual, flag, step, default=None):
    """
    Get the value of an event in a given step

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: event in a given step
    """
    try:
        return individual[flag][step]
    except IndexError:
        # if we catch an index error, this means we haven't processed that field
        return default


def calculate_time_weighted_risk_factor(events):
    """
    Given an individual's event history, calculate the time weighted risk factor

    :param events: event list
    :return: time weighted factor
    """
    numerator = sum([x * (i + 1) for i, x in enumerate(events)])
    denominator = sum([i + 1 for i in range(len(events))])

    try:
        return numerator / denominator
    except ZeroDivisionError:
        return 0


def time_weighted_risk_factor(individual, flag):
    """
    Get the time weighted risk factor for an attribute.

    :param individual: member of the population
    :param flag: key to evaluate
    :return: time weighted factor
    """
    events = get_event(individual, flag)
    return calculate_time_weighted_risk_factor(events)


def mean_risk_factor(individual, flag):
    """
    Get the mean risk factor for an attribute.

    :param individual: member of the population
    :param flag: key to evaluate
    :return: time weighted factor
    """
    events = get_event(individual, flag)
    numerator = sum([x for x in events])
    denominator = len(events)

    try:
        return numerator / denominator
    except ZeroDivisionError:
        return 0


def get_time_of_event(individual, flag):
    """
    Get the timestep of the first occurrence of an event

    :param individual: member of the population
    :param flag: key to evaluate
    :return: timestep of first occurrence
    """
    try:
        event_history = get_event(individual, flag)
        return event_history.index(1)
    except ValueError:
        return -1


def get_dcct_edic_coeff(individual):
    """
    The DCCT/EDIC flag is used to determine whether or not an individual was part
    of the DCCT/EDIC data set or EDC.

    Note: Search and Exchange data sets always use this value. This requirement
    is baked into the Search/Exchange progressions. We have to grin and bear it.

    :param individual: member of the population
    :returns: Should we use the dcct_edic factor?
    """
    value = 1
    if individual['dataset'] == 'edc':
        value = 0

    return value


def get_dcct_yearly_int_coeffs(individual, step):
    """
    Determine the yearly coefficients for dcct intervention.

    Note: Search and Exchange data sets always apply dcct_intervention. Consequently,
    we will always apply these values.

    :param individual: member of the population
    :param step: timestep
    :returns: Tuple of int_y1 and int_ay1 values
    """
    use_year_1 = 0
    use_year_after_1 = 0
    if individual['dcct_intervention']:
        if step == 1:
            use_year_1 = 1
        else:
            use_year_after_1 = 1

    return (use_year_1, use_year_after_1)


def get_1994_yearly_coeffs():
    """
    From progression notes: "These variables indicate individuals who have
    started intensive treatment long after diagnosis, which we do not expect
    for modern populations."

    Since they're "not expected", we default them to zero.
    :returns: Tuple of int_y1 and int_ay1 1994 values
    """

    return (0, 0)


def delete_last_entry(individual, event):
    event_history = individual[event]
    del event_history[-1]
    return event_history


@jit(nopython=True)
def calculate_weibull_prob_t2d(shape_val, explanators, step, lambda_val, multiplier, total_risk_reduction):

    shape = np.exp(shape_val)

    integrated_hazard_t = multiplier * weibull.model(explanators, step - 1, lambda_val, shape)
    integrated_hazard_t1 = multiplier * weibull.model(explanators, step, lambda_val, shape)

    complication_prob = 1 - np.exp(integrated_hazard_t - integrated_hazard_t1)

    return (1 - total_risk_reduction) * complication_prob

@jit(nopython=True)
def calculate_weibull_prob_t1d(shape_val, explanators, step, lambda_val, multiplier, total_risk_reduction):

    shape = shape_val

    integrated_hazard_t = multiplier * weibull.model(explanators, step - 1, lambda_val, shape)
    integrated_hazard_t1 = multiplier * weibull.model(explanators, step, lambda_val, shape)

    complication_prob = 1 - np.exp(integrated_hazard_t - integrated_hazard_t1)

    return (1 - total_risk_reduction) * complication_prob