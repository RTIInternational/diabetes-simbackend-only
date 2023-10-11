import argparse
import json
from src.orchestration.synchronous_orchestrator import SynchronousOchestrator

arg_parser = argparse.ArgumentParser(description='Comprehensive Diabetes Model')
arg_parser.add_argument('scenario', help='name of the scenario file to use')
arg_parser.add_argument('--stages', choices=['population', 'simulation', 'analysis'],
                        nargs="*",
                        default=['population', 'simulation', 'analysis'],
                        help='pipeline stages to execute (default: population simulation analysis')
arg_parser.add_argument('--uuid',
                        default='CLI',
                        help='UUID to use (default: %(default)s')
args = arg_parser.parse_args()

stages = args.stages

import time

start = time.time()

orchestrator = SynchronousOchestrator(args.uuid, stages=stages)
orchestrator.read(args.scenario)
orchestrator.run()

end = time.time()
print(end - start)
