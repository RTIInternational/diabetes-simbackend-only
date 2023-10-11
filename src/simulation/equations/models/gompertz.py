import numpy as np
from numba import jit

@jit(nopython=True)
def model(explanators, time, lambda_val, phi_val):
    """
    Calculate a Gompertz integrated hazard

    :param explanators: sum of explanatory variables
    :param time: age of individual
    :param lambda_val: lambda factor
    :param phi_val: phi factor
    :returns: Gompertz integrated hazard value
    """
    return (1.0 / phi_val) * np.exp(lambda_val + explanators) * (np.exp(phi_val * time) - 1.0)
