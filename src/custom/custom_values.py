class CustomValues:

    def __init__(self, scenario):
        self._value_dict = {'cvd_multipliers': {}, 'mortality_multipliers': {}, 'complication_multipliers': {}}
        self.scenario = scenario

        if scenario['diabetes_type'] == 't1d':
            self.calculate_t1d_values()
        elif scenario['diabetes_type'] == 't2d':
            self.calculate_t2d_values()
        elif scenario['diabetes_type'] == 'screen':
            self.calculate_screening_values()
        else:
            self.calculate_prediabetes_values()

    def calculate_t1d_values(self):
        self._value_dict['mortality_multipliers'] = self.scenario['mortality_multipliers'][0]
        self._value_dict['complication_multipliers'] = self.scenario['complication_multipliers'][0]

    def calculate_t2d_values(self):
        self._value_dict['mortality_multipliers'] = self.scenario['mortality_multipliers'][0]
        self._value_dict['complication_multipliers'] = self.scenario['complication_multipliers'][0]

    def calculate_prediabetes_values(self):
        self._value_dict['cvd_multipliers'] = self.scenario['cvd_multipliers'][0]
        self._value_dict['mortality_multipliers'] = self.scenario['mortality_multipliers'][0]
        self._value_dict['complication_multipliers'] = self.scenario['complication_multipliers'][0]

    def calculate_screening_values(self):
        self._value_dict['annual_prob_prediabetes'] = self.scenario['annual_prob_prediabetes'][0]
        self._value_dict['mortality_multipliers'] = self.scenario['mortality_multipliers'][0]
        self._value_dict['complication_multipliers'] = self.scenario['complication_multipliers'][0]

    @property
    def custom_values(self):
        return self._value_dict
