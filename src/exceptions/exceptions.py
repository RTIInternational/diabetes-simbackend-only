class ConfigurationError(Exception):
    '''
    ConfigurationError is raised when a scenario key/value pair does not adhere to
    a predefined shape.
    '''


class ModuleError(Exception):
    '''
    ModuleError is raised when an equation module is invalid
    '''


class SimulationError(Exception):
    '''
    SimulationError is raised when a simulation pipeline exits during execution.
    '''
