import numpy as np
from numba import jit

@jit(nopython=True)
def model(explanators, time, lambda_val):
    """
    Calculate an Exponential integrated hazard

    :param explanators: sum of explanatory variables
    :param time: time since diagnosis
    :param lambda_val: lambda factor
    :returns: Exponential integrated hazard value
    """
    return np.exp(lambda_val + explanators) * time
