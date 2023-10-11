class SimAgent:
    """
    The SimAgent Class stores all attributes for a particular individual in the
    population, evaluating the individuals for complications.
    """
    def __init__(self, equations, data):
        self.equations = equations
        self.timestep = 0
        self.data = data

    def step(self, rng, max_age):
        """
        Conduct a step
        """
        self.timestep += 1
        # required for max_age halting condition
        if self.data['should_update'] and self.data['age'] < max_age:
            for stage in self.equations:
                rng.shuffle(stage)
                for eq in stage:
                    eq.set_individual(self.data)
                    eq.set_step(self.timestep)
                    self.data = eq.invoke()
        else:
            self.data['should_update'] = 0
