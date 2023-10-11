import numpy as np
from numba import jit

def model(rng, upper, lower):
    """
    Calculate a uniformly distributed value

    :param explanators: sum of explanatory variables
    :param lambda_val: lambda factor
    :returns: logistic regression intergrated hazard value
    """
    return rng.uniform(upper, lower)
