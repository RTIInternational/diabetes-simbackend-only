import logging
import os
from src.configuration.configuration_manager import (ConfigurationManager,
                                                     ConfigurationError)
from src.experiments.experiment_manager import ExperimentManager
from . import (BASE_POPULATION_PATH, BASE_SIMULATION_PATH, BASE_ANALYSIS_PATH, BROADCAST_MESSAGES,
               BROADCAST_STATUSES, LOGGING_FORMAT)


def define_environment_variables():
    BASE_ANALYSIS_PATH = os.path.join('src', 'analysis', 'output')
    BASE_POPULATION_PATH = os.path.join('src', 'population', 'output')
    BASE_SIMULATION_PATH = os.path.join('src', 'simulation', 'output')
    os.environ['BASE_POPULATION_PATH'] = BASE_POPULATION_PATH
    os.environ['BASE_SIMULATION_PATH'] = BASE_SIMULATION_PATH
    os.environ['BASE_ANALYSIS_PATH'] = BASE_ANALYSIS_PATH


def _generate_output_dir(directory_path):
    """
    Create an output directory as applicable.

    :param directory_path: Directory path
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


class BaseOrchestrator():
    """
    Orchestrator manages the execution of a simulation pipeline from population
    generation to analysis.
    """

    def __init__(self, uuid):
        """
        Initialize the Orchestrator
        """
        self.configured = False
        logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
        self.logger = logging.getLogger('orchestrator')
        self.uuid = str(uuid)
        define_environment_variables()

    def _configure(self, config):
        """
        Perform common configuration tasks.

        :param config: ConfigurationManager object
        """
        self.config = config
        self.scenario = config.scenario
        self.simulations = ExperimentManager.generate_scenarios(self.scenario)

        self.configured = True
        self.broadcast(BROADCAST_MESSAGES['configuration'])

    def broadcast(self, message, message_type=BROADCAST_STATUSES['message']):
        """
        Broadcast a message to the logger and SocketHandler connection

        :param message: Message body
        :param message_type: Type of message to be broadcast.
        """
        self.logger.info('Broadcast (%s): %s - %s', message_type, message,
                         self.uuid)

    def configure(self, scenario):
        """
        Configure a scenario. This method accepts a scenario and attempts to
        validate. If the scenario is valid, save the scenario object as an instance
        variable. If it is invalid (that is, if ConfigurationError is thrown),
        broadcast the error message.

        :param scenario: Scenario file name
        """
        try:
            config = ConfigurationManager(scenario)
            self._configure(config)
        except ConfigurationError as e:
            self.broadcast(BROADCAST_MESSAGES['configuration_failed'],
                           BROADCAST_STATUSES['error'])
            raise

    def generate_output_directories(self):
        """
        Generate UUID based output directories for population generation and
        simulation tasks.
        """
        self.population_path = os.path.join(BASE_POPULATION_PATH, self.uuid)
        _generate_output_dir(self.population_path)

        self.simulation_path = os.path.join(BASE_SIMULATION_PATH, self.uuid)
        _generate_output_dir(self.simulation_path)

        self.analysis_path = os.path.join(BASE_ANALYSIS_PATH, self.uuid)
        _generate_output_dir(self.analysis_path)

    def get_population_path(self, popfile):
        """
        Get a population file path from the specified population file name

        :param popfile: population file name
        :returns: full population path
        """
        # return os.path.join(self.population_path, '{}.csv'.format(popfile))
        return os.path.join(self.population_path, f'{popfile}.pkl')

    def read(self, scenario):
        """
        Read a scenario. This method accepts a scenario and attempts to read it
        into memory. If the scenario is valid, save the scenario object as an instance
        variable. If it is invalid (that is, if ConfigurationError is thrown),
        broadcast the error message.

        :param scenario: Scenario file name
        """
        try:
            filepath = os.path.join('scenarios', '{}.json'.format(scenario))
            config = ConfigurationManager.read(filepath)
            self._configure(config)
        except ConfigurationError as e:
            self.broadcast(BROADCAST_MESSAGES['configuration_failed'],
                           BROADCAST_STATUSES['error'])
            raise

    def run(self):
        pass
