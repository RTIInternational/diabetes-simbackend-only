from copy import deepcopy
import math
import numpy as np

from src.simulation.equations.models import *
import json

class ExperimentScenario():
    def __init__(self):
        self.scenario = {}

    @property
    def seed(self):
        return self.scenario['seed']

    @seed.setter
    def seed(self, seed):
        self.scenario['seed'] = seed

    @property
    def scenario_name(self):
        return self.scenario['scenario_name']

    @scenario_name.setter
    def scenario_name(self, scenario_name):
        self.scenario['scenario_name'] = scenario_name

    @property
    def scenario_type(self):
        return self.scenario['scenario_type']

    @scenario_type.setter
    def scenario_type(self, scenario_type):
        self.scenario['scenario_type'] = scenario_type

    @property
    def population_name(self):
        return self.scenario['population']['population_name']

    @population_name.setter
    def population_name(self, population_name):
        self.scenario['population']['population_name'] = population_name

    @property
    def input_population_name(self):
        return self.scenario['input_population_name']

    @input_population_name.setter
    def input_population_name(self, input_population_name):
        self.scenario['input_population_name'] = input_population_name

    @property
    def size(self):
        return self.scenario['size']

    @size.setter
    def size(self, population_size):
        self.scenario['size'] = population_size

    @property
    def iterations(self):
        return self.scenario['iterations']

    @iterations.setter
    def iterations(self, iterations):
        self.scenario['iterations'] = iterations

    @property
    def time_horizon(self,):
        return self.scenario['time_horizon']

    @time_horizon.setter
    def time_horizon(self, time_horizon):
        self.scenario['time_horizon'] = time_horizon

    @property
    def max_steps(self,):
        return self.scenario['max_steps']

    @max_steps.setter
    def max_steps(self, max_steps):
        self.scenario['max_steps'] = max_steps

    @property
    def max_age(self):
        return self.scenario['max_age']

    @max_age.setter
    def max_age(self, age):
        self.scenario['max_age'] = age

    @property
    def diabetes_type(self):
        return self.scenario['diabetes_type']

    @diabetes_type.setter
    def diabetes_type(self, equation_set):
        self.scenario['diabetes_type'] = equation_set

    @property
    def population_dataset_uuid(self):
        return self.scenario['population_dataset_uuid']

    @population_dataset_uuid.setter
    def population_dataset_uuid(self, uuid):
        self.scenario['population_dataset_uuid'] = uuid

    @property
    def include_medicare(self):
        return self.scenario['include_medicare']

    @include_medicare.setter
    def include_medicare(self, include_medicare):
        self.scenario['include_medicare'] = include_medicare

    @property
    def intervention_status(self):
        return self.scenario['is_intervention']

    @intervention_status.setter
    def intervention_status(self, status):
        self.scenario['is_intervention'] = status

    @property
    def intervention_set(self):
        return self.scenario['intervention_set']

    @intervention_set.setter
    def intervention_set(self, intervention_set):
        self.scenario['intervention_set'] = intervention_set

    @property
    def discount(self):
        return self.scenario['economics']['discount']

    @discount.setter
    def discount(self, discount):
        self.scenario['economics']['discount'] = discount

    @property
    def baseline_economic_factors(self):
        return self.scenario['baseline_economic_factors']

    @baseline_economic_factors.setter
    def baseline_economic_factors(self, baseline_economic_factors):
        self.scenario['baseline_economic_factors'] = baseline_economic_factors

    @property
    def costs(self):
        return self.scenario['costs']

    @costs.setter
    def costs(self, costs):
        self.scenario['costs'] = costs

    @property
    def costs_medicare(self):
        return self.scenario['costs_medicare']

    @costs_medicare.setter
    def costs_medicare(self, costs_medicare):
        self.scenario['costs_medicare'] = costs_medicare

    @property
    def disutilities(self):
        return self.scenario['disutilities']

    @disutilities.setter
    def disutilities(self, disutilities):
        self.scenario['disutilities'] = disutilities
    # "psa_risk_reduction": "5%",

    @property
    def psa_intervention_costs(self):
        return self.scenario['psa_intervention_costs']

    @psa_intervention_costs.setter
    def psa_intervention_costs(self, psa_intervention_costs):
        self.scenario['psa_intervention_costs'] = psa_intervention_costs

    @property
    def psa_factor_change(self):
        return self.scenario['psa_factor_change']

    @psa_factor_change.setter
    def psa_factor_change(self, psa_factor_change):
        self.scenario['psa_factor_change'] = psa_factor_change

    @property
    def psa_risk_reduction(self):
        return self.scenario['psa_risk_reduction']

    @psa_risk_reduction.setter
    def psa_risk_reduction(self, psa_risk_reduction):
        self.scenario['psa_risk_reduction'] = psa_risk_reduction

    @property
    def psa_complication_variability(self):
        return self.scenario['psa_complication_variability']

    @psa_complication_variability.setter
    def psa_complication_variability(self, psa_complication_variability):
        self.scenario['psa_complication_variability'] = psa_complication_variability

    @property
    def psa_mortality_variability(self):
        return self.scenario['psa_mortality_variability']

    @psa_mortality_variability.setter
    def psa_mortality_variability(self, psa_mortality_variability):
        self.scenario['psa_mortality_variability'] = psa_mortality_variability

    @property
    def cost_strategy(self):
        return self.scenario['economics']['cost_strategy']

    @cost_strategy.setter
    def cost_strategy(self, cost_strategy):
        self.scenario['economics']['cost_strategy'] = cost_strategy

    @property
    def intervention_cost(self):
        return self.scenario['economics']['intervention_cost']

    @intervention_cost.setter
    def intervention_cost(self, intervention_cost):
        self.scenario['economics']['intervention_cost'] = intervention_cost

    @property
    def SEARCH_demographics(self):
        return self.scenario['SEARCH_demographics']

    @SEARCH_demographics.setter
    def SEARCH_demographics(self, search_demographics):
        self.scenario['SEARCH_demographics'] = search_demographics

    @property
    def demographics(self):
        return self.scenario['demographics']

    @demographics.setter
    def demographics(self, demographics):
        self.scenario['demographics'] = demographics

    @property
    def cvd_multipliers(self):
        return self.scenario['cvd_multipliers']

    @cvd_multipliers.setter
    def cvd_multipliers(self, cvd_multipliers):
        self.scenario['cvd_multipliers'] = cvd_multipliers

    @property
    def who_gets_screened(self):
        return self.scenario['who_gets_screened']

    @who_gets_screened.setter
    def who_gets_screened(self, who_gets_screened):
        self.scenario['who_gets_screened'] = who_gets_screened

    @property
    def non_screening_diagnosis(self):
        return self.scenario['non_screening_diagnosis']

    @non_screening_diagnosis.setter
    def non_screening_diagnosis(self, non_screening_diagnosis):
        self.scenario['non_screening_diagnosis'] = non_screening_diagnosis

    @property
    def annual_prob_prediabetes(self):
        return self.scenario['annual_prob_prediabetes']

    @annual_prob_prediabetes.setter
    def annual_prob_prediabetes(self, annual_prob_prediabetes):
        self.scenario['annual_prob_prediabetes'] = annual_prob_prediabetes

    @property
    def screening_characteristics(self):
        return self.scenario['screening_characteristics']

    @screening_characteristics.setter
    def screening_characteristics(self, screening_characteristics):
        self.scenario['screening_characteristics'] = screening_characteristics

    @property
    def complication_multipliers(self):
        return self.scenario['complication_multipliers']

    @complication_multipliers.setter
    def complication_multipliers(self, complication_multipliers):
        self.scenario['complication_multipliers'] = complication_multipliers

    @property
    def mortality_multipliers(self):
        return self.scenario['mortality_multipliers']

    @mortality_multipliers.setter
    def mortality_multipliers(self, mortality_multipliers):
        self.scenario['mortality_multipliers'] = mortality_multipliers

    @property
    def cvd_costs(self):
        return self.scenario['cvd_costs']

    @cvd_costs.setter
    def cvd_costs(self, cvd_costs):
        self.scenario['cvd_costs'] = cvd_costs

    @property
    def EXCHANGE_demographics(self):
        return self.scenario['EXCHANGE_demographics']

    @EXCHANGE_demographics.setter
    def EXCHANGE_demographics(self, exchange_demographics):
        self.scenario['EXCHANGE_demographics'] = exchange_demographics

    @property
    def population_composition(self):
        return self.scenario['population_composition']

    @population_composition.setter
    def population_composition(self, population_composition):
        self.scenario['population_composition'] = population_composition

    @property
    def risk_factors(self):
        return self.scenario['risk_factors']

    @risk_factors.setter
    def risk_factors(self, risk_factors):
        self.scenario['risk_factors'] = risk_factors

    @property
    def SEARCH_risk_factors(self):
        return self.scenario['SEARCH_risk_factors']

    @SEARCH_risk_factors.setter
    def SEARCH_risk_factors(self, search_risk_factors):
        self.scenario['SEARCH_risk_factors'] = search_risk_factors

    @property
    def EXCHANGE_risk_factors(self):
        return self.scenario['EXCHANGE_risk_factors']

    @EXCHANGE_risk_factors.setter
    def EXCHANGE_risk_factors(self, exchange_risk_factors):
        self.scenario['EXCHANGE_risk_factors'] = exchange_risk_factors

    @property
    def clinical_history(self):
        return self.scenario['clinical_history']

    @clinical_history.setter
    def clinical_history(self, clinical_history):
        self.scenario['clinical_history'] = clinical_history

    @property
    def SEARCH_clinical_history(self):
        return self.scenario['SEARCH_clinical_history']

    @SEARCH_clinical_history.setter
    def SEARCH_clinical_history(self, search_clinical_history):
        self.scenario['SEARCH_clinical_history'] = search_clinical_history

    @property
    def EXCHANGE_clinical_history(self):
        return self.scenario['EXCHANGE_clinical_history']

    @EXCHANGE_clinical_history.setter
    def EXCHANGE_clinical_history(self, exchange_clinical_history):
        self.scenario['EXCHANGE_clinical_history'] = exchange_clinical_history


class ExperimentManager:
    """
    ExperimentManager generates derived simulations from a single scenario file.
    """

    @staticmethod
    def init_scenario(base_scenario, suffix, run_id):
        scenario = ExperimentScenario()
        scenario.scenario_name = base_scenario['scenario_name'] + suffix + '--' + f"{run_id:04d}"
        scenario.scenario_type = base_scenario['simulation_type']
        scenario.input_population_name = base_scenario['scenario_name']
        scenario.size = base_scenario['size']
        scenario.iterations = base_scenario['iterations']
        scenario.time_horizon = base_scenario['time_horizon']
        scenario.diabetes_type = base_scenario['diabetes_type']
        scenario.population_dataset_uuid = base_scenario['population_dataset_uuid']
        scenario.include_medicare = base_scenario['include_medicare']
        scenario.baseline_economic_factors = base_scenario['baseline_economic_factors'][0]
        scenario.costs = base_scenario['costs'][0]
        scenario.costs_medicare = base_scenario['costs_medicare'][0]
        scenario.disutilities = base_scenario['disutilities'][0]
        scenario.mortality_multipliers = base_scenario['mortality_multipliers']
        scenario.complication_multipliers = base_scenario['complication_multipliers']
        if scenario.scenario_type == 'PSA':
            scenario.psa_intervention_costs = base_scenario['psa_intervention_costs']
            scenario.psa_factor_change = base_scenario['psa_factor_change']
            scenario.psa_risk_reduction = base_scenario['psa_risk_reduction']
            scenario.psa_complication_variability = base_scenario['psa_complication_variability']
            scenario.psa_mortality_variability = base_scenario['psa_mortality_variability']
        if scenario.population_dataset_uuid != 'none':
            scenario.demographics = {}
            scenario.risk_factors = {}
            scenario.clinical_history = {}
        else:
            scenario.demographics = base_scenario['demographics']
            scenario.risk_factors = base_scenario['risk_factors']
            scenario.clinical_history = base_scenario['clinical_history']
        scenario.intervention_status = False
        scenario.economics = None

        if scenario.time_horizon == 'fixed':
            scenario.max_steps = base_scenario['max_steps']
        if scenario.time_horizon == 'max_age':
            scenario.max_age = base_scenario['max_age']
        else:
            scenario.horizon_limit = 0

        return scenario

    @classmethod
    def psa_basic_interventions(cls, rng, interventions, psa_risk, psa_cost, psa_factor):
        # We have input value, which is usually a risk reduction (e.g., a 49% risk reduction)
        # and selected significance value. Convert risk reduction to a relative risk (=mean);
        # e.g, 49% risk reduction = 0.51 relative risk (= 1 – risk reduction).
        # Distribution is lognormal. Apply normal(ln(mean), [-ln(mean)/Z]). After draw, exponentiate the value.

        modified_interventions = deepcopy(interventions)
        z_dict = {1: 2.57, 5: 1.960, 10: 1.645}

        if psa_factor != 'Do not vary' and 'lifestyle_control_intervention' in modified_interventions.keys():
            setup_type = modified_interventions['lifestyle_control_intervention']['lifestyle_control_setup_type']
            if setup_type == 'basic':
                intervention_name = 'lifestyle_control_intervention'
                lifestyle = modified_interventions[intervention_name][intervention_name][0]
                year_1 = lifestyle['year_1_change']
                subsequent = lifestyle['year_subsequent_change']
                new_year_1 = normal.model(rng, year_1, abs(year_1) / z_dict[int(psa_factor)], 4)
                new_subsequent = normal.model(rng, subsequent, abs(subsequent) / z_dict[int(psa_factor)], 4)
                lifestyle['year_1_change'] = round(new_year_1, 2)
                lifestyle['year_subsequent_change'] = round(new_subsequent, 2)

        if psa_risk != 'Do not vary':
            for intervention_short_name in ['generic_control', 'glycemic_control', 'cholesterol_control', 'bp_control']:
                intervention_name = intervention_short_name + '_intervention'
                intervention_type = intervention_short_name + '_setup_type'
                if intervention_name in interventions.keys():
                    if intervention_name == 'generic_control_intervention':
                        setup_type = 'basic'
                    else:
                        setup_type = modified_interventions[intervention_name][intervention_type]
                    if setup_type == 'basic':
                        # only pulls in risk reductions
                        intervention = modified_interventions[intervention_name][intervention_name][0]
                        risk_reductions = intervention['risk_reductions']
                        updated_values = {}
                        for risk, value in risk_reductions.items():
                            if value != 0:
                                relative_risk = 1 - value
                                if value < 1:
                                    log_value = math.log(relative_risk)
                                else:
                                    log_value = -18.42
                                new_value = normal.model(rng, log_value, - log_value / z_dict[int(psa_risk)], 4)
                                new_value = 1 - math.exp(new_value)
                                updated_values[risk] = round(new_value, 2)
                            else:
                                updated_values[risk] = value
                        intervention['risk_reductions'] = updated_values

        if psa_cost != 'Do not vary':
            psa_cost = int(psa_cost) / 100
            name = 'lifestyle_control_intervention'
            if name in modified_interventions.keys():
                setup_type = modified_interventions[name]['lifestyle_control_setup_type']
                if setup_type == 'basic':
                    year_1_cost = modified_interventions[name][name][0]['year_1_cost']
                    subsequent_years_cost = modified_interventions[name][name][0]['subsequent_years_cost']
                    # if scenario['scenario_type'] == 'PSA' and psa_cost != 'Do not vary':
                    # user does not enter a % value but only selects from several options; these options are
                    # expressed as digits (not decimals)
                    # psa_change = int(''.join(filter(str.isdigit, scenario['psa_intervention_costs']))) / 100
                    new_year_1_cost = uniform.model(rng, (1 - psa_cost) * year_1_cost, (1 + psa_cost) * year_1_cost)
                    new_subsequent_cost = uniform.model(rng, (1 - psa_cost) * subsequent_years_cost,
                                                        (1 + psa_cost) * subsequent_years_cost)
                    modified_interventions[name][name][0]['year_1_cost'] = round(new_year_1_cost)
                    modified_interventions[name][name][0]['subsequent_years_cost'] = int(round(new_subsequent_cost))

            else:
                for type in ['generic', 'glycemic', 'cholesterol', 'bp']:
                    name = f'{type}_control_intervention'
                    if name in modified_interventions.keys():
                        if name == 'generic_control_intervention':
                            setup_type = 'basic'
                        else:
                            setup_type = modified_interventions[name][f'{type}_control_setup_type']
                        if setup_type == 'basic':
                            cost = modified_interventions[name][name][0]['annual_cost']
                            # if scenario['scenario_type'] == 'PSA' and psa_cost != 'Do not vary':
                            # user does not enter a % value but only selects from several options; these options are
                            # expressed as digits (not decimals)
                            # psa_change = int(''.join(filter(str.isdigit, scenario['psa_intervention_costs']))) / 100
                            new_cost = uniform.model(rng, (1 - psa_cost) * cost, (1 + psa_cost) * cost)
                            modified_interventions[name][name][0]['annual_cost'] = int(round(new_cost))

        return modified_interventions

    @classmethod
    def psa_advanced_interventions(cls, rng, interventions, psa_factor, psa_cost):

        z_dict = {1: 2.57, 5: 1.960, 10: 1.645}
        do_factor_psa = True
        do_cost_psa = True
        if psa_factor == 'Do not vary':
            do_factor_psa = False
        if psa_cost == 'Do not vary':
            do_cost_psa = False
        else:
            psa_cost = int(psa_cost) / 100

        def _modify_glycemic(intervention):
            if intervention['glycemic_control_setup_type'] == 'basic':
                return intervention
            modified_intervention = deepcopy(intervention)

            if do_factor_psa:
                intensifications = modified_intervention['glycemic_control_intensification_advanced'][0]
                for seq_id in ['', 'next', 'subsequent']:
                    if seq_id == '':
                        std_intensification = intensifications[f'Effect of intensifying on A1c Standard']
                        intervention_intensification = intensifications[f'Effect of intensifying on A1c Intervention']
                    else:
                        std_intensification = intensifications[f'Effect of {seq_id} intensification on A1c Standard']
                        intervention_intensification = intensifications[f'Effect of {seq_id} intensification on A1c Intervention']
                    dif = intervention_intensification - std_intensification
                    value = normal.model(rng, dif, abs(dif / z_dict[int(psa_factor)]), 4)
                    intense_value = - round(std_intensification + value, 2)
                    if seq_id == '':
                        intensifications[f'Effect of intensifying on A1c Intervention'] = intense_value
                    else:
                        intensifications[f'Effect of {seq_id} intensification on A1c Intervention'] = intense_value
                modified_intervention['glycemic_control_intensification_advanced'][0] = intensifications

            if do_cost_psa:
                costs = modified_intervention['glycemic_control_costs_advanced'][0]
                for seq_id in ['Current', 'First', 'Next', 'Subsequent']:
                    if seq_id == 'Current':
                        std_cost = costs['Current treatment Standard']
                        intervention_cost = costs['Current treatment Intervention']
                    else:
                        std_cost = costs[f'{seq_id} intensification Standard']
                        intervention_cost = costs[f'{seq_id} intensification Intervention']
                    dif = abs(intervention_cost - std_cost)
                    if dif > 0:
                        value = uniform.model(rng, (1 - psa_cost) * dif, (1 + psa_cost) * dif)
                        new_cost_value = int(round(std_cost + value, 0))
                        if seq_id == 'Current':
                            costs['Current treatment Intervention'] = new_cost_value
                        else:
                            costs[f'{seq_id} intensification Intervention'] = new_cost_value
                modified_intervention['glycemic_control_costs_advanced'][0] = costs

            return modified_intervention

        def _modify_bp(intervention):
            if intervention['bp_control_setup_type'] == 'basic':
                return intervention
            modified_intervention = deepcopy(intervention)

            if do_factor_psa:
                intensifications = modified_intervention['bp_control_intensification_advanced'][0]
                for seq_id in ['first', 'second', 'subsequent']:
                    std_intensification = intensifications[f'Effect of {seq_id} drug on blood pressure Standard']
                    intervention_intensification = intensifications[f'Effect of {seq_id} drug on blood pressure Intervention']
                    dif = intervention_intensification - std_intensification
                    value = normal.model(rng, dif, abs(dif / z_dict[int(psa_factor)]), 4)
                    intense_value = round(std_intensification + value, 2)
                    intensifications[f'Effect of {seq_id} drug on blood pressure Intervention'] = intense_value
                modified_intervention['bp_control_intensification_advanced'][0] = intensifications

            if do_cost_psa:
                costs = modified_intervention['bp_control_costs_advanced'][0]
                for seq_id in ['Current', 'First', 'Next', 'Subsequent']:
                    if seq_id == 'Current':
                        std_cost = costs['Current treatment Standard']
                        intervention_cost = costs['Current treatment Intervention']
                    else:
                        std_cost = costs[f'{seq_id} intensification Standard']
                        intervention_cost = costs[f'{seq_id} intensification Intervention']
                    dif = abs(intervention_cost - std_cost)
                    if dif > 0:
                        value = uniform.model(rng, (1 - psa_cost) * dif, (1 + psa_cost) * dif)
                        new_cost_value = int(round(std_cost + value, 0))
                        if seq_id == 'Current':
                            costs['Current treatment Intervention'] = new_cost_value
                        else:
                            costs[f'{seq_id} intensification Intervention'] = new_cost_value
                modified_intervention['bp_control_costs_advanced'][0] = costs

            return modified_intervention

        def _modify_cholesterol(intervention):
            if intervention['cholesterol_control_setup_type'] == 'basic':
                return intervention
            modified_intervention = deepcopy(intervention)

            if do_cost_psa:
                costs = modified_intervention['cholesterol_control_costs_advanced'][0]
                moderate_cost = costs['Moderate intensity statin']
                high_cost = costs['High intensity statin']
                new_moderate_cost = uniform.model(rng, (1 - psa_cost) * moderate_cost, (1 + psa_cost) * moderate_cost)
                new_high_cost = uniform.model(rng, (1 - psa_cost) * high_cost, (1 + psa_cost) * high_cost)
                costs['Moderate intensity statin'] = int(round(new_moderate_cost, 0))
                costs['High intensity statin'] = int(round(new_high_cost, 0))
                modified_intervention['cholesterol_control_costs_advanced'][0] = costs
            return modified_intervention

        def _modify_lifestyle(intervention):
            if intervention['lifestyle_control_setup_type'] == 'basic':
                return intervention
            modified_intervention = deepcopy(intervention)
            return modified_intervention

        if 'glycemic_control_intervention' in interventions.keys():
            glycemic_intervention = interventions['glycemic_control_intervention']
            interventions['glycemic_control_intervention'] = _modify_glycemic(glycemic_intervention)
        if 'bp_control_intervention' in interventions.keys():
            bp_intervention = interventions['bp_control_intervention']
            interventions['bp_control_intervention'] = _modify_bp(bp_intervention)
        if 'cholesterol_control_intervention' in interventions.keys():
            cholesterol_intervention = interventions['cholesterol_control_intervention']
            interventions['cholesterol_control_intervention'] = _modify_cholesterol(cholesterol_intervention)
        if 'lifestyle_control_intervention' in interventions.keys():
            lifestyle_intervention = interventions['lifestyle_control_intervention']
            interventions['lifestyle_control_intervention'] = _modify_lifestyle(lifestyle_intervention)

        return interventions

    @classmethod
    def generate_scenarios(cls, base_scenario):
        """
        Generate scenario permutations from experiments

        :returns: list of configurations
        """

        scenario_manifest = {}
        interventions = base_scenario['intervention_types'][0]
        # looks like we don't actually need to check for no-intervention scenarios
        # I'll leave the code in until we are absolutely sure
        intervention_types = [val for key, val in interventions.items() if 'type' in key]
        has_interventions = all([elem for elem in intervention_types])

        # generate a list of size=iterations of random numbers based on configured seed
        rng = np.random.default_rng(base_scenario['seed'])
        psa_rng = np.random.default_rng(base_scenario['seed'])
        seed_list = rng.integers(low=1, high=2 ** 16, size=base_scenario['iterations'] + 1)

        for run_id in range(1, base_scenario['iterations'] + 1):
            scenario_list = []
            for run_type in ['__non-intervention', '__intervention']:
                scenario = cls.init_scenario(base_scenario, run_type, run_id)

                scenario.intervention_set = {}

                scenario.intervention_status = False
                if run_type == '__intervention':
                    scenario.intervention_status = True

                scenario.scenario_name = scenario.scenario_name

                scenario.seed = int(seed_list[run_id])

                # interventions are not hierarchically ordered in json so we need to do this here
                # one dictionary per interventions type: generic, glycemic, cholesterol
                # since advanced interventions also modify non-intervention runs, interventions are always added
                intervention_list = []
                generic_dict = {'intervention_name': 'generic control intervention'}
                glycemic_dict = {'intervention_name': 'glycemic control intervention'}
                cholesterol_dict = {'intervention_name': 'cholesterol control intervention'}
                bp_dict = {'intervention_name': 'bp control intervention'}
                smoking_dict = {'intervention_name': 'smoking control intervention'}
                lifestyle_dict = {'intervention_name': 'lifestyle control intervention'}
                intervention_type_dicts = {'generic': generic_dict, 'glycemic': glycemic_dict, 'cholesterol': cholesterol_dict,
                                           'bp': bp_dict, 'smoking': smoking_dict, 'lifestyle': lifestyle_dict}
                intervention_type_mapping = {'generic': 'generic_control_intervention', 'glycemic': 'glycemic_control_intervention',
                                             'cholesterol': 'cholesterol_control_intervention', 'bp': 'bp_control_intervention',
                                             'smoking': 'smoking_control_intervention',
                                             'lifestyle': 'lifestyle_control_intervention'}
                all_interventions = {}
                for intervention_type in intervention_type_dicts.keys():
                    intervention_dict = intervention_type_dicts[intervention_type]
                    for key, value in base_scenario.items():
                        if intervention_type in key:
                            intervention_dict[key] = value
                            all_interventions[intervention_type_mapping[intervention_type]] = intervention_dict
                # add the list of all those interventions that are actually applied
                all_interventions['interventions_basic'] = base_scenario['intervention_types']
                intervention_list.append(all_interventions)

                base_intervention_set = {'interventions': intervention_list}
                intervention_set = deepcopy(base_intervention_set)
                if base_scenario['simulation_type'] == 'PSA' and run_type == '__intervention':
                    psa_factor = base_scenario['psa_factor_change']
                    psa_risk = base_scenario['psa_risk_reduction']
                    psa_cost = base_scenario['psa_intervention_costs']
                    interventions = intervention_set['interventions'][0]
                    # an intervention set may contain basic and advanced interventions
                    # since the {basic, advanced} setting is intervention specific we don't split the modification
                    # here; the respective intervention code checks for {basic, advanced}
                    basic_interventions = cls.psa_basic_interventions(psa_rng, interventions,
                                                                      psa_risk,
                                                                      psa_cost,
                                                                      psa_factor)
                    # note: 'interventions' contains information about basic and advanced interventions (a scenario
                    # can have both types of interventions) so update basic first and then feed that into the
                    # advanced setup
                    advanced_interventions = cls.psa_advanced_interventions(psa_rng, basic_interventions,
                                                                            psa_factor,
                                                                            psa_cost)
                    # note: the second dictionary takes precedence
                    intervention_set['interventions'][0] = advanced_interventions
                # originally the experiment manager generated different scenarios for non-intervention and
                # intervention runs; it is much easier to avoid this and simply let the analysis use the
                # 'is intervention' flag to distinguish the two
                scenario.intervention_set = intervention_set
                scenario_list.append(scenario.scenario)
            scenario_manifest[run_id] = scenario_list

        return scenario_manifest
