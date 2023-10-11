import numpy as np
from numba import jit

@jit(nopython=True)
def model(explanators, lambda_val):
    """
    Calculate a logistic integrated hazard

    :param explanators: sum of explanatory variables
    :param lambda_val: lambda factor
    :returns: logistic regression intergrated hazard value
    """
    z = (lambda_val + explanators)
    return 1 / (1 + np.exp(-z))
