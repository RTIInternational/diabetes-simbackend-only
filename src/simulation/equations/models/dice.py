import numpy as np


def model(rng, value):
    """
    Throw a dice

    :returns: [0, 1]
    """
    return 1 if value >= rng.random() else 0
