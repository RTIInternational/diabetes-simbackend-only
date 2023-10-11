import numpy as np
import math
from numba import jit

def model(rng, mean, se, decimals):
    """
    Draw a value from a gamma distribution

    :param mean
    :param se
    :param decimals
    :returns: beta distributed value
    """

    if mean == 0:
        return 0
    elif se == 0:
        return mean
    else:
        sign = 1
        if mean < 0:
            mean = abs(mean)
            sign = -1
        alpha = mean * ((mean * (1 - mean)) / (se ** 2) - 1)
        beta = (mean * ((mean * (1 - mean)) / (se ** 2) - 1)) * ((1 - mean) / mean)
        return sign * round(rng.beta(alpha, beta), decimals)
