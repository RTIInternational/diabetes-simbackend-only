import numpy as np
from numba import jit

def model(rng, mu, sig, decimals):
    """
    Draw a value from a gamma distribution

    :param mu
    :param sig
    :param decimals
    :returns: gamma distributed value
    """
    # shape = mu ** 2 / sig ** 2
    # scale = sig ** 2 / mu
    # return round(rng.gamma(shape, scale), decimals)
    try:
        shape = mu ** 2 / sig ** 2
        scale = sig ** 2 / mu
        return round(rng.gamma(shape, scale), decimals)
    except ZeroDivisionError:
        return 0
