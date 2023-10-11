import numpy as np
from numba import jit

def model(rng, mean, std_dev, decimals):
    """
    Calculate a normally distributed value

    :param explanators: sum of explanatory variables
    :param lambda_val: lambda factor
    :returns: logistic regression intergrated hazard value
    """
    return round(rng.normal(mean, std_dev), decimals)
