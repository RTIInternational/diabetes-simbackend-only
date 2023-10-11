import argparse
import os
import sys
import jsonschema
import json


def get_json(json_path):
    loaded_json = {}
    try:
        with open(json_path, 'r') as raw_json:
            loaded_json = json.load(raw_json)
    except FileNotFoundError as e:
        # print('JSON file at \'{}\' does not exist.'.format(json_path))
        sys.exit(1)

    return loaded_json


def main():
    arg_parser = argparse.ArgumentParser(description='Schema Valdiation')
    arg_parser.add_argument('-s',
                            '--scenario',
                            help='Scenario file name')
    args = arg_parser.parse_args()

    base_dir = os.path.join(os.path.dirname(__file__), '..')
    schema_dir = os.path.join(base_dir, 'src', 'schemas')
    schema_path = os.path.join(schema_dir, 'schema.json')

    schema = get_json(schema_path)

    scenario_path = os.path.join(base_dir, 'scenarios', '{}.json'.format(args.scenario))
    scenario = get_json(scenario_path)

    resolver_url = 'file://{}/'.format(os.path.abspath(schema_dir))
    resolver = jsonschema.RefResolver(base_uri=resolver_url, referrer=schema)

    try:
        jsonschema.validate(scenario, schema, resolver=resolver)
        print('{}.json is valid.'.format(args.scenario))
        sys.exit(0)
    except jsonschema.exceptions.ValidationError as e:
        print('{}.json is invalid.'.format(args.scenario))
        # print(e.message)
        sys.exit(1)
    except jsonschema.exceptions.RefResolutionError as e:
        print(str(e))


if __name__ == "__main__":
    main()
