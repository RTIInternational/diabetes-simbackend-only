EVENT = "lifespan"

IS_DETERMINISTIC = True

BEHAVIOR = 'SET'


def calculate(individual, step, *_):
    """
    Increment an individual's lifespan
    """
    return individual['lifespan'] + 1


def modify_coefficients(data, rng):
    pass