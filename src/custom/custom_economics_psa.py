from src.simulation.equations.models import *


class CustomEconomics:

    def __init__(self, rng, scenario):
        self.scenario = scenario
        self.rng = rng

        if scenario['diabetes_type'] == 't1d':
            self._value_dict = {'include_medicare': scenario['include_medicare'], 'costs': {}, 'costs_medicare': {},
                                'disutilities': {},
                                'intervention costs': {}}
            self.calculate_t1d_values(self.rng)
        elif scenario['diabetes_type'] == 't2d':
            self._value_dict = {'include_medicare': scenario['include_medicare'], 'costs': {}, 'costs_medicare': {},
                                'disutilities': {},
                                'intervention costs': {}}
            self.calculate_t2d_values(self.rng)
        elif scenario['diabetes_type'] == 'screen':
            self._value_dict = {'include_medicare': scenario['include_medicare'], 'pre_screen_costs': {}, 'costs': {},
                                'costs_medicare': {}, 'pre_screen_disutilities': {},
                                'disutilities': {}, 'intervention costs': {}}
            self.calculate_prediabetes_screening_values(self.rng)
        else:
            self._value_dict = {'include_medicare': scenario['include_medicare'], 'pre_costs': {}, 'costs': {},
                                'costs_medicare': {}, 'pre_disutilities': {}, 'disutilities': {},
                                'intervention costs': {}}
            self.calculate_prediabetes_values(self.rng)

    def get_interventions_costs(self, scenario):

        interventions = scenario['intervention_set']['interventions'][0]

        all_cost_dict = {}

        # basic cost
        for type in ['generic', 'glycemic', 'cholesterol', 'bp']:
            name = f'{type}_control_intervention'
            if name in interventions.keys():
                if name == 'generic_control_intervention':
                    setup_type = 'basic'
                else:
                    setup_type = interventions[name][f'{type}_control_setup_type']
                if setup_type == 'basic':
                    cost = interventions[name][name][0]['annual_cost']
                    all_cost_dict[f'baseline {type} intervention'] = cost

        if 'smoking_control_intervention' in interventions.keys():
            cost = interventions['smoking_control_intervention']['smoking_control_intervention'][0]['annual_cost']
            all_cost_dict['smoking'] = cost

        # advanced cost from here on
        for type in ['glycemic', 'bp']:
            name = f'{type}_control_intervention'
            if name in interventions.keys():
                setup_type = interventions[name][f'{type}_control_setup_type']
                if setup_type == 'advanced':
                    intervention_costs = interventions[f'{type}_control_intervention'][f'{type}_control_costs_advanced'][0]
                    cost_dict = {
                        'default standard': intervention_costs['Current treatment Standard'],
                        'default intervention': intervention_costs['Current treatment Intervention'],
                        'drug 1 standard': intervention_costs['First intensification Standard'],
                        'drug 1 intervention': intervention_costs['First intensification Intervention'],
                        'drug 2 standard': intervention_costs['Next intensification Standard'],
                        'drug 2 intervention': intervention_costs['Next intensification Intervention'],
                        'drug 3 standard': intervention_costs['Subsequent intensification Standard'],
                        'drug 3 intervention': intervention_costs['Subsequent intensification Intervention'],
                    }
                    all_cost_dict[type] = cost_dict

        if 'cholesterol_control_intervention' in interventions.keys():
            name = 'cholesterol_control_intervention'
            setup_type = interventions[name]['cholesterol_control_setup_type']
            if setup_type == 'advanced':
                chol_intervention_costs = interventions[name]['cholesterol_control_costs_advanced'][0]
                statin_dict = {'1': chol_intervention_costs['Moderate intensity statin'], '2': chol_intervention_costs['High intensity statin']}
                all_cost_dict['statin type'] = statin_dict

        if 'lifestyle_control_intervention' in interventions.keys():
            lifestyle_type = interventions['lifestyle_control_intervention']['lifestyle_control_setup_type']
            if lifestyle_type == 'basic':
                lifestyle_basic_costs = interventions['lifestyle_control_intervention']['lifestyle_control_intervention'][0]
                lifestyle_dict = {
                    'type': lifestyle_type,
                    'basic year 1': lifestyle_basic_costs['year_1_cost'],
                    'basic year subsequent': lifestyle_basic_costs['subsequent_years_cost']
                }
            else:
                lifestyle_advanced_costs = interventions['lifestyle_control_intervention']['lifestyle_control_costs'][0]
                lifestyle_dict = {
                    'type': lifestyle_type,
                    'advanced year 1': lifestyle_advanced_costs['year_1_cost'],
                    'advanced year 2': lifestyle_advanced_costs['year_2_cost'],
                    'advanced year 3': lifestyle_advanced_costs['year_3_cost'],
                    'advanced year subsequent': lifestyle_advanced_costs['subsequent_year_cost']
                }
            all_cost_dict['lifestyle'] = lifestyle_dict

        return all_cost_dict

    def calculate_t1d_values(self, rng):

        self._value_dict['intervention costs'] = self.get_interventions_costs(self.scenario)

        self._value_dict['costs']['death_cost'] = self.scenario['costs']['Incremental cost in year of death cost']
        self._value_dict['costs']['discount factor'] = self.scenario['baseline_economic_factors']['Cost discount factor']
        self._value_dict['costs']['cost discount factor'] = self.scenario['baseline_economic_factors']['Cost discount factor']

        self._value_dict['costs']['microalbuminuria'] = (0, 0)
        self._value_dict['costs']['npdr'] = (0, 0)

        base_cost = self.scenario['costs']['Base cost']
        base_cost_se = self.scenario['costs']['Base cost se']
        time_varying_cost = self.scenario['costs']['TV age cost']
        time_varying_cost_se = self.scenario['costs']['TV age cost se']
        self._value_dict['costs']['base cost'] = gamma.model(rng, base_cost, base_cost_se, 0)
        self._value_dict['costs']['age cost'] = gamma.model(rng, time_varying_cost, time_varying_cost_se, 0)

        entries = ['DKA', 'Amputation', 'CSME', 'Hypoglycemia']
        labels = ['dka', 'amputation', 'csme', 'hypoglycemia']
        for entry, label in zip(entries, labels):
            cost = self.scenario['costs'][f'{entry}, first year cost']
            se = self.scenario['costs'][f'{entry}, first year se']
            first = gamma.model(rng, cost, se, 0)
            self._value_dict['costs'][label] = (first, 0)

        entries = ['Macroalbuminuria', 'GFR', 'ESRD', 'DPN', 'PDR', 'Ulcer', 'CVD MACE', 'CVD non-MACE']
        labels = ['macroalbuminuria', 'gfr', 'esrd', 'dpn', 'pdr', 'ulcer', 'cvd_mace', 'cvd_non_mace']
        for entry, label in zip(entries, labels):
            first_year_mean = self.scenario['costs'][f'{entry}, first year cost']
            first_year_se = self.scenario['costs'][f'{entry}, first year se']
            following_year_mean = self.scenario['costs'][f'{entry}, following year cost']
            following_year_se = self.scenario['costs'][f'{entry}, following year se']
            first_year_cost = gamma.model(rng, first_year_mean, first_year_se, 0)
            following_year_cost = gamma.model(rng, following_year_mean, following_year_se, 0)
            self._value_dict['costs'][label] = (first_year_cost, following_year_cost)

        self._value_dict['costs_medicare']['death_cost'] = self.scenario['costs']['Incremental cost in year of death cost']
        self._value_dict['costs_medicare']['cost discount factor'] = self.scenario['baseline_economic_factors'][
            'Cost discount factor']

        self._value_dict['costs_medicare']['microalbuminuria'] = (0, 0)
        self._value_dict['costs_medicare']['npdr'] = (0, 0)

        base_cost = self.scenario['costs_medicare']['Base cost']
        base_cost_se = self.scenario['costs_medicare']['Base cost se']
        time_varying_cost = self.scenario['costs_medicare']['TV age cost']
        time_varying_cost_se = self.scenario['costs_medicare']['TV age cost se']
        self._value_dict['costs_medicare']['base cost'] = gamma.model(rng, base_cost, base_cost_se, 0)
        self._value_dict['costs_medicare']['age cost'] = gamma.model(rng, time_varying_cost, time_varying_cost_se, 0)

        entries = ['DKA', 'Amputation', 'CSME', 'Hypoglycemia']
        labels = ['dka', 'amputation', 'csme', 'hypoglycemia']
        for entry, label in zip(entries, labels):
            cost = self.scenario['costs_medicare'][f'{entry}, first year cost']
            se = self.scenario['costs_medicare'][f'{entry}, first year se']
            first = gamma.model(rng, cost, se, 0)
            self._value_dict['costs_medicare'][label] = (first, 0)

        entries = ['Macroalbuminuria', 'GFR', 'ESRD', 'DPN', 'PDR', 'Ulcer', 'CVD MACE', 'CVD non-MACE']
        labels = ['macroalbuminuria', 'gfr', 'esrd', 'dpn', 'pdr', 'ulcer', 'cvd_mace', 'cvd_non_mace']
        for entry, label in zip(entries, labels):
            first_year_mean = self.scenario['costs_medicare'][f'{entry}, first year cost']
            first_year_se = self.scenario['costs_medicare'][f'{entry}, first year se']
            following_year_mean = self.scenario['costs_medicare'][f'{entry}, following year cost']
            following_year_se = self.scenario['costs_medicare'][f'{entry}, following year se']
            first_year_cost = gamma.model(rng, first_year_mean, first_year_se, 0)
            following_year_cost = gamma.model(rng, following_year_mean, following_year_se, 0)
            self._value_dict['costs_medicare'][label] = (first_year_cost, following_year_cost)

        entries = ['Baseline QALY', 'Age', 'Female', 'Baseline duration']
        labels = ['base qaly', 'age', 'female', 'diabetes_duration_entry']
        for entry, label in zip(entries, labels):
            self._value_dict['disutilities'][label] = self.scenario['disutilities'][entry]
        self._value_dict['disutilities']['qaly discount factor'] = self.scenario['baseline_economic_factors']['QALY discount factor']

        entries = ['Ulcer', 'Hypoglycemia', 'DKA']
        labels = ['ulcer', 'hypoglycemia', 'dka']
        for entry, label in zip(entries, labels):
            first = self.scenario['disutilities'][f'{entry}, first year mean']
            se = self.scenario['disutilities'][f'{entry}, first year se']
            qaly_first = beta.model(rng,  first, se, 4)
            self._value_dict['disutilities'][label] = (qaly_first, 0)

        entries = ['Microalbuminuria', 'Macroalbuminuria', 'Impaired GFR', 'ESRD',
                   'NPDR', 'PDR', 'CSME', 'CVD MACE', 'CVD non-MACE', 'DPN', 'Amputation']
        labels = ['microalbuminuria', 'macroalbuminuria', 'gfr', 'esrd', 'npdr',
                  'pdr', 'csme', 'cvd_mace', 'cvd_non_mace', 'dpn', 'amputation']
        for entry, label in zip(entries, labels):
            first = self.scenario['disutilities'][f'{entry}, first year mean']
            se_first = self.scenario['disutilities'][f'{entry}, first year se']
            following = self.scenario['disutilities'][f'{entry}, following year mean']
            se_following = self.scenario['disutilities'][f'{entry}, following year se']
            qaly_first = beta.model(rng,  first, se_first, 4)
            qaly_following = beta.model(rng,  following, se_following, 4)
            self._value_dict['disutilities'][label] = (qaly_first, qaly_following)

    def calculate_t2d_values(self, rng):

        self._value_dict['intervention costs'] = self.get_interventions_costs(self.scenario)

        self._value_dict['costs']['base cost'] = self.scenario['costs']['Base cost']
        self._value_dict['costs']['death_cost'] = self.scenario['costs']['Incremental cost in year of death cost']
        self._value_dict['costs']['cost discount factor'] = self.scenario['baseline_economic_factors']['Cost discount factor']
        self._value_dict['costs']['microalbuminuria'] = (0, 0)
        self._value_dict['costs']['hypoglycemia_any'] = (0, 0)

        base_cost = self.scenario['costs']['Base cost']
        base_cost_se = self.scenario['costs']['Base cost se']
        time_varying_cost = self.scenario['costs']['TV age cost']
        time_varying_cost_se = self.scenario['costs']['TV age cost se']
        self._value_dict['costs']['base cost'] = gamma.model(rng, base_cost, base_cost_se, 0)
        self._value_dict['costs']['age cost'] = normal.model(rng, time_varying_cost, time_varying_cost_se, 0)

        entries = ['Amputation', 'Revascularization', 'Angina', 'Hypoglycemia (medical assistance)']
        labels = ['amputation', 'revasc', 'angina', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            cost = self.scenario['costs'][f'{entry}, first year cost']
            se = self.scenario['costs'][f'{entry}, first year se']
            first = gamma.model(rng, cost, se, 0)
            self._value_dict['costs'][label] = (first, 0)

        entries = ['Macroalbuminuria', 'eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy', 'Laser retina', 'Foot ulcer',
                   'Blindness',
                   'MI', 'Stroke', 'CHF']
        labels = ['macroalbuminuria', 'egfr_60', 'egfr_30', 'dialysis', 'neurop', 'laser_retina', 'ulcer',
                  'blindness', 'mi', 'stroke', 'chf']
        for entry, label in zip(entries, labels):
            first_year_mean = self.scenario['costs'][f'{entry}, first year cost']
            first_year_se = self.scenario['costs'][f'{entry}, first year se']
            following_year_mean = self.scenario['costs'][f'{entry}, following year cost']
            following_year_se = self.scenario['costs'][f'{entry}, following year se']
            first_year_cost = gamma.model(rng, first_year_mean, first_year_se, 0)
            following_year_cost = gamma.model(rng, following_year_mean, following_year_se, 0)
            self._value_dict['costs'][label] = (first_year_cost, following_year_cost)

        self._value_dict['costs_medicare']['base cost'] = self.scenario['costs_medicare']['Base cost']
        self._value_dict['costs_medicare']['death_cost'] = self.scenario['costs_medicare']['Incremental cost in year of death cost']
        self._value_dict['costs_medicare']['cost discount factor'] = self.scenario['baseline_economic_factors'][
            'Cost discount factor']

        self._value_dict['costs_medicare']['death_cost'] = self.scenario['costs'][
            'Incremental cost in year of death cost']
        self._value_dict['costs_medicare']['cost discount factor'] = self.scenario['baseline_economic_factors'][
            'Cost discount factor']

        self._value_dict['costs_medicare']['microalbuminuria'] = (0, 0)
        self._value_dict['costs_medicare']['npdr'] = (0, 0)

        base_cost = self.scenario['costs_medicare']['Base cost']
        base_cost_se = self.scenario['costs_medicare']['Base cost se']
        time_varying_cost = self.scenario['costs_medicare']['TV age cost']
        time_varying_cost_se = self.scenario['costs_medicare']['TV age cost se']
        self._value_dict['costs_medicare']['base cost'] = gamma.model(rng, base_cost, base_cost_se, 0)
        self._value_dict['costs_medicare']['age cost'] = normal.model(rng, time_varying_cost, time_varying_cost_se, 0)

        entries = ['Amputation', 'Revascularization', 'Angina', 'Hypoglycemia (medical assistance)']
        labels = ['amputation', 'revasc', 'angina', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            cost = self.scenario['costs_medicare'][f'{entry}, first year cost']
            se = self.scenario['costs_medicare'][f'{entry}, first year se']
            first = gamma.model(rng, cost, se, 0)
            self._value_dict['costs_medicare'][label] = (first, 0)

        entries = ['Macroalbuminuria', 'eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy', 'Laser retina', 'Foot ulcer',
                   'Blindness',
                   'MI', 'Stroke', 'CHF']
        labels = ['macroalbuminuria', 'egfr_60', 'egfr_30', 'dialysis', 'neurop', 'laser_retina', 'ulcer',
                  'blindness', 'mi', 'stroke', 'chf']
        for entry, label in zip(entries, labels):
            first_year_mean = self.scenario['costs_medicare'][f'{entry}, first year cost']
            first_year_se = self.scenario['costs_medicare'][f'{entry}, first year se']
            following_year_mean = self.scenario['costs_medicare'][f'{entry}, following year cost']
            following_year_se = self.scenario['costs_medicare'][f'{entry}, following year se']
            first_year_cost = gamma.model(rng, first_year_mean, first_year_se, 0)
            following_year_cost = gamma.model(rng, following_year_mean, following_year_se, 0)
            self._value_dict['costs_medicare'][label] = (first_year_cost, following_year_cost)

        self._value_dict['disutilities']['qaly discount factor'] = self.scenario['baseline_economic_factors'][
            'QALY discount factor']
        self._value_dict['disutilities']['base qaly'] = self.scenario['disutilities']['Baseline QALY']
        self._value_dict['disutilities']['hypoglycemia_any'] = (0, 0)

        entries = ['Smoking', 'BMI', 'Duration', 'Hypoglycemia (medical assistance)']
        labels = ['smoker', 'bmi', 'diabetes_duration_entry', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            first = self.scenario['disutilities'][f'{entry}, first year mean']
            se = self.scenario['disutilities'][f'{entry}, first year se']
            qaly_first = beta.model(rng, first, se, 4)
            self._value_dict['disutilities'][label] = (qaly_first, 0)

        entries = ['eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy',
                   'Foot ulcer', 'Amputation', 'Laser retina',
                   'Blindness', 'MI', 'Stroke', 'CHF', 'Angina',
                   'Revascularization']
        labels = ['egfr_60', 'egfr_30', 'dialysis', 'neurop',
                  'ulcer', 'amputation', 'laser_retina',
                  'blindness', 'mi', 'stroke', 'chf', 'angina',
                  'revasc']
        for entry, label in zip(entries, labels):
            first = self.scenario['disutilities'][f'{entry}, first year mean']
            se_first = self.scenario['disutilities'][f'{entry}, first year se']
            following = self.scenario['disutilities'][f'{entry}, following year mean']
            se_following = self.scenario['disutilities'][f'{entry}, following year se']
            qaly_first = beta.model(rng,  first, se_first, 4)
            qaly_following = beta.model(rng,  following, se_following, 4)
            self._value_dict['disutilities'][label] = (qaly_first, qaly_following)

    def calculate_prediabetes_values(self, rng):

        self._value_dict['intervention costs'] = self.get_interventions_costs(self.scenario)

        pre_disutilities = self.scenario['cvd_costs'][0]
        self._value_dict['pre_disutilities']['base qaly'] = pre_disutilities['baseline_qaly']
        self._value_dict['pre_disutilities']['bmi'] = pre_disutilities['bmi']
        self._value_dict['pre_disutilities']['diabetes_duration_entry'] = pre_disutilities['duration_in_analysis']
        pre_costs = self.scenario['cvd_costs'][1]
        self._value_dict['pre_costs']['base cost normoglycemia'] = pre_costs['base_cost_normoglycemia']
        self._value_dict['pre_costs']['base cost prediabetes'] = pre_costs['base_cost_prediabetes']
        self._value_dict['pre_costs']['age cost'] = pre_costs['tv_age_cost']

        self._value_dict['costs']['death_cost'] = self.scenario['costs']['Incremental cost in year of death cost']
        self._value_dict['costs']['cost discount factor'] = self.scenario['baseline_economic_factors']['Cost discount factor']        

        self._value_dict['costs']['microalbuminuria'] = (0, 0)
        self._value_dict['costs']['hypoglycemia_any'] = (0, 0)

        base_cost = self.scenario['costs']['Base cost']
        base_cost_se = self.scenario['costs']['Base cost se']
        time_varying_cost = self.scenario['costs']['TV age cost']
        time_varying_cost_se = self.scenario['costs']['TV age cost se']
        self._value_dict['costs']['base cost'] = gamma.model(rng, base_cost, base_cost_se, 0)
        self._value_dict['costs']['age cost'] = normal.model(rng, time_varying_cost, time_varying_cost_se, 0)

        entries = ['Amputation', 'Revascularization', 'Angina', 'Hypoglycemia (medical assistance)']
        labels = ['amputation', 'revasc', 'angina', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            cost = self.scenario['costs'][f'{entry}, first year cost']
            se = self.scenario['costs'][f'{entry}, first year se']
            first = gamma.model(rng, cost, se, 0)
            self._value_dict['costs'][label] = (first, 0)

        entries = ['Macroalbuminuria', 'eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy', 'Laser retina', 'Foot ulcer',
                   'Blindness', 'MI', 'Stroke', 'CHF']
        labels = ['macroalbuminuria', 'egfr_60', 'egfr_30', 'dialysis', 'neurop', 'laser_retina', 'ulcer',
                  'blindness', 'mi', 'stroke', 'chf']
        for entry, label in zip(entries, labels):
            first_year_mean = self.scenario['costs'][f'{entry}, first year cost']
            first_year_se = self.scenario['costs'][f'{entry}, first year se']
            following_year_mean = self.scenario['costs'][f'{entry}, following year cost']
            following_year_se = self.scenario['costs'][f'{entry}, following year se']
            first_year_cost = gamma.model(rng, first_year_mean, first_year_se, 0)
            following_year_cost = gamma.model(rng, following_year_mean, following_year_se, 0)
            self._value_dict['costs'][label] = (first_year_cost, following_year_cost)

        self._value_dict['costs_medicare']['death_cost'] = self.scenario['costs']['Incremental cost in year of death cost']
        self._value_dict['costs_medicare']['cost discount factor'] = self.scenario['baseline_economic_factors'][
            'Cost discount factor']

        self._value_dict['costs_medicare']['microalbuminuria'] = (0, 0)
        self._value_dict['costs_medicare']['hypoglycemia_any'] = (0, 0)

        base_cost = self.scenario['costs_medicare']['Base cost']
        base_cost_se = self.scenario['costs_medicare']['Base cost se']
        time_varying_cost = self.scenario['costs_medicare']['TV age cost']
        time_varying_cost_se = self.scenario['costs_medicare']['TV age cost se']
        self._value_dict['costs_medicare']['base cost'] = gamma.model(rng, base_cost, base_cost_se, 0)
        self._value_dict['costs_medicare']['age cost'] = normal.model(rng, time_varying_cost, time_varying_cost_se, 0)

        entries = ['Amputation', 'Revascularization', 'Angina', 'Hypoglycemia (medical assistance)']
        labels = ['amputation', 'revasc', 'angina', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            cost = self.scenario['costs_medicare'][f'{entry}, first year cost']
            se = self.scenario['costs_medicare'][f'{entry}, first year se']
            first = gamma.model(rng, cost, se, 0)
            self._value_dict['costs_medicare'][label] = (first, 0)

        entries = ['Macroalbuminuria', 'eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy', 'Laser retina', 'Foot ulcer',
                   'Blindness', 'MI', 'Stroke', 'CHF']
        labels = ['macroalbuminuria', 'egfr_60', 'egfr_30', 'dialysis', 'neurop', 'laser_retina', 'ulcer',
                  'blindness', 'mi', 'stroke', 'chf']
        for entry, label in zip(entries, labels):
            first_year_mean = self.scenario['costs_medicare'][f'{entry}, first year cost']
            first_year_se = self.scenario['costs_medicare'][f'{entry}, first year se']
            following_year_mean = self.scenario['costs_medicare'][f'{entry}, following year cost']
            following_year_se = self.scenario['costs_medicare'][f'{entry}, following year se']
            first_year_cost = gamma.model(rng, first_year_mean, first_year_se, 0)
            following_year_cost = gamma.model(rng, following_year_mean, following_year_se, 0)
            self._value_dict['costs_medicare'][label] = (first_year_cost, following_year_cost)

        self._value_dict['disutilities']['qaly discount factor'] = self.scenario['baseline_economic_factors'][
            'QALY discount factor']
        self._value_dict['disutilities']['base qaly'] = self.scenario['disutilities']['Baseline QALY']
        self._value_dict['disutilities']['hypoglycemia_any'] = (0, 0)

        entries = ['Smoking', 'BMI', 'Duration', 'Hypoglycemia (medical assistance)']
        labels = ['smoker', 'bmi', 'diabetes_duration_entry', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            first = self.scenario['disutilities'][f'{entry}, first year mean']
            se = self.scenario['disutilities'][f'{entry}, first year se']
            qaly_first = beta.model(rng, first, se, 4)
            self._value_dict['disutilities'][label] = (qaly_first, 0)

        entries = ['eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy', 'Foot ulcer', 'Amputation', 'Laser retina',
                   'Blindness', 'MI', 'Stroke', 'CHF', 'Angina', 'Revascularization']
        labels = ['egfr_60', 'egfr_30', 'dialysis', 'neurop', 'ulcer', 'amputation', 'laser_retina',
                  'blindness', 'mi', 'stroke', 'chf', 'angina', 'revasc']
        
        for entry, label in zip(entries, labels):
            first = self.scenario['disutilities'][f'{entry}, first year mean']
            se_first = self.scenario['disutilities'][f'{entry}, first year se']
            following = self.scenario['disutilities'][f'{entry}, following year mean']
            se_following = self.scenario['disutilities'][f'{entry}, following year se']
            qaly_first = beta.model(rng, first, se_first, 4)
            qaly_following = beta.model(rng, following, se_following, 4)
            self._value_dict['disutilities'][label] = (qaly_first, qaly_following)

    def calculate_prediabetes_screening_values(self, rng):

        self._value_dict['intervention costs'] = self.get_interventions_costs(self.scenario)
        print(self._value_dict['intervention costs'])

        # pre-diabetes cost
        pre_screen_disutilities = self.scenario['cvd_costs'][0]
        self._value_dict['pre_screen_disutilities']['base qaly'] = pre_screen_disutilities['baseline_qaly']
        self._value_dict['pre_screen_disutilities']['bmi'] = pre_screen_disutilities['bmi']
        self._value_dict['pre_screen_disutilities']['diabetes_duration_entry'] = pre_screen_disutilities[
            'duration_in_analysis']

        screening_costs = self.scenario['screening_characteristics'][0]
        self._value_dict['pre_screen_costs']['cost_screening'] = screening_costs['cost_screening']
        self._value_dict['pre_screen_costs']['cost_confirmatory'] = screening_costs['cost_confirmatory']

        pre_costs = self.scenario['cvd_costs'][1]
        self._value_dict['pre_screen_costs']['base cost normoglycemia'] = pre_costs['base_cost_normoglycemia']
        # note: this is NOT the actual screening cost; it is just base cost following the naming convention
        self._value_dict['pre_screen_costs']['base cost screening'] = pre_costs['base_cost_screening']
        self._value_dict['pre_screen_costs']['age cost'] = pre_costs['tv_age_cost']
        self._value_dict['pre_screen_costs']['age cost'] = pre_costs['tv_age_cost']

        self._value_dict['costs']['death_cost'] = self.scenario['costs']['Incremental cost in year of death cost']
        self._value_dict['costs']['cost discount factor'] = self.scenario['baseline_economic_factors'][
            'Cost discount factor']

        self._value_dict['costs']['microalbuminuria'] = (0, 0)
        self._value_dict['costs']['hypoglycemia_any'] = (0, 0)

        base_cost = self.scenario['costs']['Base cost']
        base_cost_se = self.scenario['costs']['Base cost se']
        time_varying_cost = self.scenario['costs']['TV age cost']
        time_varying_cost_se = self.scenario['costs']['TV age cost se']
        self._value_dict['costs']['base cost'] = gamma.model(rng, base_cost, base_cost_se, 0)
        self._value_dict['costs']['age cost'] = normal.model(rng, time_varying_cost, time_varying_cost_se, 0)

        entries = ['Amputation', 'Revascularization', 'Angina', 'Hypoglycemia (medical assistance)']
        labels = ['amputation', 'revasc', 'angina', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            cost = self.scenario['costs'][f'{entry}, first year cost']
            se = self.scenario['costs'][f'{entry}, first year se']
            first = gamma.model(rng, cost, se, 0)
            self._value_dict['costs'][label] = (first, 0)

        entries = ['Macroalbuminuria', 'eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy', 'Laser retina', 'Foot ulcer',
                   'Blindness', 'MI', 'Stroke', 'CHF']
        labels = ['macroalbuminuria', 'egfr_60', 'egfr_30', 'dialysis', 'neurop', 'laser_retina', 'ulcer',
                  'blindness', 'mi', 'stroke', 'chf']
        for entry, label in zip(entries, labels):
            first_year_mean = self.scenario['costs'][f'{entry}, first year cost']
            first_year_se = self.scenario['costs'][f'{entry}, first year se']
            following_year_mean = self.scenario['costs'][f'{entry}, following year cost']
            following_year_se = self.scenario['costs'][f'{entry}, following year se']
            first_year_cost = gamma.model(rng, first_year_mean, first_year_se, 0)
            following_year_cost = gamma.model(rng, following_year_mean, following_year_se, 0)
            self._value_dict['costs'][label] = (first_year_cost, following_year_cost)

        self._value_dict['costs_medicare']['death_cost'] = self.scenario['costs'][
            'Incremental cost in year of death cost']
        self._value_dict['costs_medicare']['cost discount factor'] = self.scenario['baseline_economic_factors'][
            'Cost discount factor']

        self._value_dict['costs_medicare']['microalbuminuria'] = (0, 0)
        self._value_dict['costs_medicare']['hypoglycemia_any'] = (0, 0)

        base_cost = self.scenario['costs_medicare']['Base cost']
        base_cost_se = self.scenario['costs_medicare']['Base cost se']
        time_varying_cost = self.scenario['costs_medicare']['TV age cost']
        time_varying_cost_se = self.scenario['costs_medicare']['TV age cost se']
        self._value_dict['costs_medicare']['base cost'] = gamma.model(rng, base_cost, base_cost_se, 0)
        self._value_dict['costs_medicare']['age cost'] = normal.model(rng, time_varying_cost, time_varying_cost_se, 0)

        entries = ['Amputation', 'Revascularization', 'Angina', 'Hypoglycemia (medical assistance)']
        labels = ['amputation', 'revasc', 'angina', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            cost = self.scenario['costs_medicare'][f'{entry}, first year cost']
            se = self.scenario['costs_medicare'][f'{entry}, first year se']
            first = gamma.model(rng, cost, se, 0)
            self._value_dict['costs_medicare'][label] = (first, 0)

        entries = ['Macroalbuminuria', 'eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy', 'Laser retina', 'Foot ulcer',
                   'Blindness', 'MI', 'Stroke', 'CHF']
        labels = ['macroalbuminuria', 'egfr_60', 'egfr_30', 'dialysis', 'neurop', 'laser_retina', 'ulcer',
                  'blindness', 'mi', 'stroke', 'chf']
        for entry, label in zip(entries, labels):
            first_year_mean = self.scenario['costs_medicare'][f'{entry}, first year cost']
            first_year_se = self.scenario['costs_medicare'][f'{entry}, first year se']
            following_year_mean = self.scenario['costs_medicare'][f'{entry}, following year cost']
            following_year_se = self.scenario['costs_medicare'][f'{entry}, following year se']
            first_year_cost = gamma.model(rng, first_year_mean, first_year_se, 0)
            following_year_cost = gamma.model(rng, following_year_mean, following_year_se, 0)
            self._value_dict['costs_medicare'][label] = (first_year_cost, following_year_cost)

        self._value_dict['disutilities']['qaly discount factor'] = self.scenario['baseline_economic_factors'][
            'QALY discount factor']
        self._value_dict['disutilities']['base qaly'] = self.scenario['disutilities']['Baseline QALY']
        self._value_dict['disutilities']['hypoglycemia_any'] = (0, 0)

        entries = ['Smoking', 'BMI', 'Duration', 'Hypoglycemia (medical assistance)']
        labels = ['smoker', 'bmi', 'diabetes_duration_entry', 'hypoglycemia_medical']
        for entry, label in zip(entries, labels):
            first = self.scenario['disutilities'][f'{entry}, first year mean']
            se = self.scenario['disutilities'][f'{entry}, first year se']
            qaly_first = beta.model(rng, first, se, 4)
            self._value_dict['disutilities'][label] = (qaly_first, 0)

        entries = ['eGFR 60', 'eGFR 30', 'Dialysis', 'Neuropathy', 'Foot ulcer', 'Amputation', 'Laser retina',
                   'Blindness', 'MI', 'Stroke', 'CHF', 'Angina', 'Revascularization']
        labels = ['egfr_60', 'egfr_30', 'dialysis', 'neurop', 'ulcer', 'amputation', 'laser_retina',
                  'blindness', 'mi', 'stroke', 'chf', 'angina', 'revasc']

        for entry, label in zip(entries, labels):
            first = self.scenario['disutilities'][f'{entry}, first year mean']
            se_first = self.scenario['disutilities'][f'{entry}, first year se']
            following = self.scenario['disutilities'][f'{entry}, following year mean']
            se_following = self.scenario['disutilities'][f'{entry}, following year se']
            qaly_first = beta.model(rng, first, se_first, 4)
            qaly_following = beta.model(rng, following, se_following, 4)
            self._value_dict['disutilities'][label] = (qaly_first, qaly_following)



    @property
    def economics(self):
        return self._value_dict
