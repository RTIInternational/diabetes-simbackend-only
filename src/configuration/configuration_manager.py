import os
import json
import jsonschema
from src.exceptions.exceptions import ConfigurationError


BASE_DIR = os.path.join('scenarios')

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(SRC_DIR, 'schemas')
SCHEMA_RESOLVER_URI = 'file://{}/'.format(os.path.abspath(SCHEMA_DIR))
SCHEMA = None
with open(os.path.join(SCHEMA_DIR, 'schema.json'), 'r') as raw_schema:
    SCHEMA = json.load(raw_schema)


class ConfigurationManager():
    """
    ConfigurationManager ingests, imports, exports, and validates simulation
    scenario files.
    """

    def __init__(self, scenario):
        self.validate(scenario)

    @staticmethod
    def strip_suffixes(scenario):
        """
        strip suffixes because internally we don't need them
        """

        diabetes_type = scenario['diabetes_type']
        for old_key, _ in list(scenario.items()):
            # remove the count variable -- it is not used
            if old_key == "intervention_sets_t1d":
                scenario.pop(old_key)
                continue
            if diabetes_type == 'pre' and 'prediabetes' in old_key:
                new_key = old_key.split('_' + diabetes_type)[0]
                new_key += '_prediabetes'
            else:
                new_key = old_key.split('_' + diabetes_type)[0]
            scenario[new_key] = scenario.pop(old_key)
        return scenario

    @classmethod
    def read(cls, filepath, **kwargs):
        """
        Read a scenario file from disc. If the scenario is valid, this method
        returns an instance of ConfigurationManager. validate() will throw
        exceptions if the scenario doesn't adhere to the prescribed shape.

        :param filename: Name of the scenario file
        :returns: new instance of ConfigurationManager
        """
        try:
            with open(filepath, 'r') as f:
                scenario = json.load(f)
            return cls(scenario, **kwargs)
        except FileNotFoundError:
            raise ConfigurationError(f'Scenario file "{filepath}" does not exist')

    def validate(self, scenario):
        """
        Validate a scenario, comparing it against a prescribed shape file. Return
        True if valid, otherwise throw the appropriate exception(s).

        :param scenario: Scenario dict for evaluation
        :param shapes: Prescribed shape object
        :returns: True if valid
        """
        resolver = jsonschema.RefResolver(base_uri=SCHEMA_RESOLVER_URI, referrer=SCHEMA)

        try:
            jsonschema.validate(scenario, SCHEMA, resolver=resolver)
        except jsonschema.exceptions.ValidationError as e:
            raise ConfigurationError(f'Validation Failed. {e.message}')
        else:
            self.scenario = self.strip_suffixes(scenario)

    def write(self, directory, filename=None):
        """
        Write a scenario to disc
        """
        if not filename:
            filename = self.scenario['scenario_name']

        filepath = os.path.join(directory, f'{filename}.json')

        with open(filepath, 'w') as f:
            json.dump(self.scenario, f)
