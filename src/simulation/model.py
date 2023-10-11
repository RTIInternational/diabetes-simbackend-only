import ast
import os
from importlib import import_module

import numpy as np
import pandas as pd

from src.custom import custom_economics, custom_economics_psa, custom_values
from src.exceptions.exceptions import SimulationError
from src.simulation.agents import SimAgent
from src.simulation.equation_factory import EquationFactory

import pyarrow.feather as feather

# CDC python container in openshift
if os.path.isdir('/opt/app-root/src'):
    BASE_PATH = os.path.abspath('/opt/app-root/src')
    BASE_DIR = os.path.join(BASE_PATH, 'src')

# RTI python container in docker
else:
    BASE_DIR = os.path.join('src')

INPUT_DIR = os.path.join(BASE_DIR, 'population', 'output')
OUTPUT_DIR = os.path.join(BASE_DIR, 'simulation', 'output')


class ComprehensiveModel:
    def __init__(self, scenario, uuid):
        self.scenario = scenario
        self.uuid = uuid
        self.agents = []
        self.running = True
        self.timestep = 0
        self.economics = None
        self.equations = None
        self.seed = scenario['seed']
        self.rng = np.random.default_rng(self.seed)
        self.psa_custom_economics_rng = np.random.default_rng(self.seed)
        if scenario['scenario_type'] == 'PSA':
            self.ce = custom_economics_psa.CustomEconomics(self.psa_custom_economics_rng, scenario)
        else:
            self.ce = custom_economics.CustomEconomics(scenario)
        self.va = custom_values.CustomValues(scenario)
        self.set_scenario(scenario)

    @property
    def agent_ages(self):
        return set([agent.data['age'] for agent in self.living_agents])

    @property
    def agent_buffer(self):
        for agent in self.agents:
            yield agent

    @property
    def agent_count(self):
        return len(self.agents)

    @property
    def agent_data(self):
        return [agent.data for agent in self.agents]

    @property
    def updatable_agents(self):
        return [agent for agent in self.agents if agent.data['should_update'] == 1]

    @property
    def living_agents(self):
        return [agent for agent in self.agents if agent.data['deceased'] == 0]

    def _should_stop_deceased_strategy(self):
        """
        Using the 'all_deceased' strategy, check if execution should stop
        """
        if len(self.living_agents) == 0:
            return True

        return False

    def _should_stop_fixed_strategy(self):
        """
        Using the 'fixed' strategy, check if execution should stop
        """
        if self._should_stop_deceased_strategy():
            return True

        if self.timestep >= self.max_steps:
            return True

        return False

    def _should_stop_maxage_strategy(self):
        """
        Using the 'max_age' strategy, check if execution should stop
        """
        if self._should_stop_deceased_strategy():
            return True

        if len(self.updatable_agents) == 0:
            return True

        return False

    def run_model(self):
        """
        Run the model and log the results
        """
        while True:
            self.timestep += 1
            self.step()

            if self.should_stop_execution():
                break

        self.write_population()

    def set_scenario(self, scenario):
        """
        Set the analysis scenario

        :param scenario: Scenario file to parse
        """

        self.set_scenario_name(scenario['scenario_name'])
        self.time_horizon = scenario['time_horizon']
        if 'max_steps' in scenario:
            self.max_steps = scenario['max_steps']
        elif 'max_age' in scenario:
            self.max_age = scenario['max_age']
        else:
            pass
        self.set_economics()
        self.set_custom_values()
        self.set_interventions(scenario['intervention_set'])
        self.set_equations(scenario['diabetes_type'])
        self.set_population(scenario['scenario_name'])

    def calculate_risk_reductions(self, diabetes_type):
        """
        :param diabetes_type:
        :return: {risk_factor:{intervention: reduction, reductions}, risk_factor:{intervention: reduction, reductions}}
        """

        if diabetes_type == 't1d':
            complication_dict = {'microalbuminuria': "microalbuminuria", 'macroalbuminuria': "macroalbuminuria",
                                 'gfr': "gfr", 'esrd': "esrd", 'npdr': "npdr", 'pdr': "pdr", 'csme': "csme",
                                 'amputation': "amputation", 'hypoglycemia': "hypoglycemia", 'dka': "dka",
                                 'ulcer': "ulcer", 'dpn': "dpn", 'cvd_non_mace': 'cvd_non_mace',
                                 'cvd_mace': 'cvd_mace'}
        else:
            complication_dict = {'microalbuminuria': "microalbuminuria", 'macroalbuminuria': "macroalbuminuria",
                                 'egfr_60': "egfr_60", 'egfr_30': "egfr_30", 'dialysis': "dialysis",
                                 'neuropathy': "neurop", 'ulcer': "ulcer", 'amputation': "amputation",
                                 'laser_retin': "laser_retina", 'blindness': "blindness", 'mi': "mi",
                                 'stroke': "stroke", 'chf': "chf", 'angina': "angina", 'revasc': "revasc",
                                 "hypo_med": 'hypoglycemia_medical', "hypo_any": 'hypoglycemia_any'}

        risk_reduction_dict = {}
        for intervention_short_name in ['generic_control', 'glycemic_control', 'cholesterol_control', 'bp_control']:
            intervention_name = intervention_short_name + '_intervention'
            intervention_type = intervention_short_name + '_setup_type'
            if intervention_name in self.interventions.keys():
                if intervention_name == 'generic_control_intervention':
                    setup_type = 'basic'
                else:
                    setup_type = self.interventions[intervention_name][intervention_type]
                if setup_type == 'basic':
                    # only pulls in risk reductions
                    intervention = self.interventions[intervention_name][intervention_name][0]
                    risk_reductions = intervention['risk_reductions']
                    for complication, reduction in risk_reductions.items():
                        complication_name = 'complication_' + complication_dict[complication]
                        if complication_name in risk_reduction_dict.keys():
                            this_intervention_dict = risk_reduction_dict[complication_name]
                            this_intervention_dict[intervention_name] = reduction
                            risk_reduction_dict[complication_name] = this_intervention_dict
                        else:
                            risk_reduction_dict[complication_name] = {intervention_name: reduction}

        return risk_reduction_dict

    def set_equations(self, equation_set):
        """
        Set the equations to be run.

        :param equation_set: one of {pre, t2d, t1d, screen}
        """

        set_module = import_module('src.simulation.equations.{}'.format(equation_set))

        equation_list = []
        risk_reduction_dict = self.calculate_risk_reductions(equation_set)

        for stage in set_module.STAGES:
            # Prepare an equation stage object
            equation_stage = []

            # Iterate over all equations in a stage
            for eq in stage:
                # Should we process this equation, adding it to our manifest?
                should_process = True

                # Set the equation module, raising if it is invalid
                try:
                    module = import_module(f'src.simulation.equations.{equation_set}.{eq}')
                    if self.scenario['scenario_type'] == 'PSA' and self.scenario['diabetes_type'] == 'screen' and eq == 'screening':
                        module.modify_coefficients({'who_gets_screened': self.scenario['who_gets_screened'],
                                                    'screening_characteristics':
                                                        self.scenario['screening_characteristics']}, self.rng)
                    elif self.scenario['scenario_type'] == 'PSA' and self.scenario['diabetes_type'] == 'screen' and eq == 'non-screening-diagnosis':
                        module.modify_coefficients({'non_screening_diagnosis': self.scenario['non_screening_diagnosis']}, self.rng)
                    elif self.scenario['scenario_type'] == 'PSA':
                        if 'mortality' in eq:
                            mortality_rng = np.random.default_rng(self.scenario['seed'])
                            module.modify_coefficients(self.scenario['psa_mortality_variability'], mortality_rng)
                        else:
                            complication_rng = np.random.default_rng(self.scenario['seed'])
                            module.modify_coefficients(self.scenario['psa_complication_variability'], complication_rng)
                    elif self.scenario['diabetes_type'] == 'screen' and eq == 'screening':
                        module.modify_coefficients({'who_gets_screened': self.scenario['who_gets_screened'],
                                                    'screening_characteristics':
                                                        self.scenario['screening_characteristics']}, self.rng)
                    elif self.scenario['diabetes_type'] == 'screen' and eq == 'non-screening-diagnosis':
                        module.modify_coefficients({'non_screening_diagnosis': self.scenario['non_screening_diagnosis']}, self.rng)
                    else:
                        module.modify_coefficients(False, None)
                except ModuleNotFoundError:
                    should_process = False
                    pass
                if should_process:
                    has_intervention = True
                    if 'non' in self.scenario_name:
                        has_intervention = False
                    # add risk reductions to equations
                    if eq in risk_reduction_dict.keys():
                        reductions = {'risk reductions': risk_reduction_dict[eq]}
                        # bp intervention has sbp condition for application
                        if 'bp_control_intervention' in self.interventions.keys():
                            name = 'bp_control_intervention'
                            type = self.interventions[name]['bp_control_setup_type']
                            if type == 'basic':
                                sbp_condition = self.interventions[name][name][0]['apply if greater than']
                                reductions['sbp_condition'] = sbp_condition
                        # cholesterol intervention has max age condition for application
                        if 'cholesterol_control_intervention' in self.interventions.keys():
                            name = 'cholesterol_control_intervention'
                            type = self.interventions[name]['cholesterol_control_setup_type']
                            if type == 'basic':
                                min_age = self.interventions[name][name][0]['age']
                                reductions['cholesterol min age'] = min_age
                        equation = EquationFactory(self.rng, module, self.uuid, self.custom_values, reductions, has_intervention)
                        equation_stage.append(equation)
                    elif eq in ['progression_hba1c'] and 'glycemic_control_intervention' in self.interventions.keys():
                        hba1c_intervention = self.interventions['glycemic_control_intervention']
                        equation = EquationFactory(self.rng, module, self.uuid, None, hba1c_intervention, has_intervention)
                    elif eq in ['progression_ldl'] and 'cholesterol_control_intervention' in self.interventions.keys():
                        cholesterol_intervention = self.interventions['cholesterol_control_intervention']
                        equation = EquationFactory(self.rng, module, self.uuid, None, cholesterol_intervention, has_intervention)
                    elif eq in ['progression_sbp_post_tx', 'progression_sbp'] and 'bp_control_intervention' \
                            in self.interventions.keys():
                        sbp_intervention = self.interventions['bp_control_intervention']
                        equation = EquationFactory(self.rng, module, self.uuid, None, sbp_intervention, has_intervention)
                    elif eq == 'progression_quit_smoking' and 'smoking_control_intervention' in self.interventions.keys():
                        # smoking intervention has no advanced setup; non-intervention run is not changed; only
                        # actual intervention run has the intervention
                        if has_intervention:
                            smoking_intervention = self.interventions['smoking_control_intervention']
                            equation = EquationFactory(self.rng, module, self.uuid, None, smoking_intervention, has_intervention)
                        else:
                            equation = EquationFactory(self.rng, module, self.uuid, None, None, has_intervention)
                    elif eq == 'complication_prediabetes':
                        equation = EquationFactory(self.rng, module, self.uuid, self.custom_values, self.interventions, has_intervention)
                    elif eq == 'complication_diabetes' and 'lifestyle_control_intervention' in self.interventions.keys():
                        lifestyle_intervention = self.interventions['lifestyle_control_intervention']
                        equation = EquationFactory(self.rng, module, self.uuid, self.custom_values, lifestyle_intervention, has_intervention)
                    elif 'economics' in eq:
                        equation = EquationFactory(self.rng, module, self.uuid, self.economics, self.interventions, has_intervention)
                    # only applies to pre-diabetes
                    # make sure to not override complications with basic interventions
                    elif equation_set == 'pre' and eq in ['complication_angina', 'complication_chf', 'complication_mi',
                                'complication_revasc', 'complication_stroke'] and eq not in risk_reduction_dict.keys():
                        equation = EquationFactory(self.rng, module, self.uuid, self.custom_values, None, has_intervention)
                    elif 'mortality' in eq:
                        equation = EquationFactory(self.rng, module, self.uuid, self.custom_values, None, has_intervention)
                    else:
                        equation = EquationFactory(self.rng, module, self.uuid, self.custom_values, None, has_intervention)

                    equation_stage.append(equation)
            equation_list.append(equation_stage)

        if not equation_list:
            raise SimulationError("No Modules to Execute")

        self.equations = equation_list

    def set_economics(self):
        self.economics = self.ce.economics

    def set_custom_values(self):
        self.custom_values = self.va.custom_values

    def set_interventions(self, interventions):
        """
        Set the interventions to be applied.

        :param interventions: list of interventions
        """
        self.interventions = interventions['interventions'][0]

    def set_population(self, population_name):
        """
        Set the baseline population

        :param population: path to a CSV to be used as baseline population
        """
        # population_path = os.path.join(INPUT_DIR, self.uuid, f'{population_name}.csv')
        population_path_pickle = os.path.join(INPUT_DIR, self.uuid, f'{population_name}.pkl')
        # population = pd.read_csv(population_path)
        population = pd.read_pickle(population_path_pickle)

        def _add_agent(row):
            """
            Add an agent to the simulation. To do this, we have to convert the
            data types through literal_eval. Most columns will pass straight
            through this eval, with the exception of event columns. Events are
            string representations of lists. This process converts the list-like
            string to an actual list.

            :param row: An individual in the population
            """
            data = {}
            for k, v in row.items():
                try:
                    data[k] = ast.literal_eval(v)
                except SyntaxError as e:
                    data[k] = None
                except ValueError as e:
                    data[k] = v

            agent = SimAgent(self.equations, data)
            self.agents.append(agent)

        self.fieldnames = population.columns.values
        population.apply(lambda x: _add_agent(x), axis=1)

    def set_scenario_name(self, scenario_name):
        """
        Set the scenario name

        :param scenario_name: Name of the scenario
        """
        self.scenario_name = scenario_name

    def should_stop_execution(self):
        """
        Should the execution continue?
        """
        if self.time_horizon == 'fixed':
            return self._should_stop_fixed_strategy()
        elif self.time_horizon == 'all_deceased':
            return self._should_stop_deceased_strategy()
        elif self.time_horizon == 'max_age':
            return self._should_stop_maxage_strategy()

        return True

    def step(self):
        """
        Simulate a step
        """
        for agent in self.agent_buffer:
            # only the max_age strategy changes this value; 1000 is used to make sure max_age does not interfere with
            # the other strategies
            max_age = 1000
            if self.time_horizon == 'max_age':
                max_age = self.max_age
            agent.step(self.rng, max_age)

    def write_population(self):
        """
        Write the simulation results to disc
        """
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        csv_output_path = os.path.join(OUTPUT_DIR, self.uuid, f'{self.scenario_name}.csv')
        output_path = os.path.join(OUTPUT_DIR, self.uuid, f'{self.scenario_name}.pkl')
        feather_path = os.path.join(OUTPUT_DIR, self.uuid, f'{self.scenario_name}.feather')

        sim_df = pd.DataFrame(self.agent_data, columns=self.fieldnames)
        # sim_df.to_csv(csv_output_path, index=False)
        sim_df.to_pickle(output_path)
        # would be ideal to use but arrow feather does not support lists as values in a df
        # feather.write_feather(sim_df, feather_path)
