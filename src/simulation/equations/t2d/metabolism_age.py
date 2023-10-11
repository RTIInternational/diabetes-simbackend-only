EVENT = "age"

IS_DETERMINISTIC = True

BEHAVIOR = 'SET'


def calculate(individual, step, *_):
    """
    Increment an individual's "age_entry":
    """
    return individual['age'] + 1


def modify_coefficients(data, rng):
    pass