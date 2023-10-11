import os
# from dotenv import load_dotenv
# load_dotenv()

BROADCAST_MESSAGES = {
    'configuration': 'Scenario Configured',
    'configuration_failed': 'Scenario Not Configured',
    'pending': 'Simulation Pending',
    'generation': 'Generating Population',
    'economics': 'Populating custom economics',
    'simulation': 'Running Simulation',
    'analysis': 'Analyzing Results',
    'executing': 'Executing',
    'done': 'Run Complete',
    'failed': 'Simulation Failed'
}

BROADCAST_STATUSES = {
    'error': 'Error',
    'message': 'Message'
}

BASE_ANALYSIS_PATH = os.path.join('src', 'analysis', 'output')
BASE_POPULATION_PATH = os.path.join('src', 'population', 'output')
BASE_SIMULATION_PATH = os.path.join('src', 'simulation', 'output')

LOGGING_FORMAT = '%(asctime)-15s %(message)s'
