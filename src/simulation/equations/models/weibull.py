import numpy as np
import warnings
from numba import jit

@jit(nopython=True)
def model(explanators, time, lambda_val, shape):
    """
    Calculate a Weibull integrated hazard

    :param explanators: sum of explanatory variables
    :param time: time since diagnosis
    :param lambda_val: lambda factor
    :param rho_val: rho factor
    :returns: Weibull integrated hazard value
    """
    return np.exp(lambda_val + explanators) * np.power(time, shape)
