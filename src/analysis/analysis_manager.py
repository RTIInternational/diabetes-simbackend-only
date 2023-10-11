from .simulation_analyzer import SimulationAnalyzer
from .psa_analyzer import PSAAnalyzer


class AnalysisManager():
    """
    AnalysisManager is a Factory class used to invoke the appropriate analysis type
    """

    def __init__(self, scenario, uuid):
        self.uuid = uuid
        self.scenario = scenario

        self._set_analysis()

    def _set_analysis(self):
        analyzer = SimulationAnalyzer

        # PSA specific analysis is not currently required; future requirements might include PSA
        # specific analysis so we leave this here
        # if self.scenario['simulation_type'] == 'PSA':
        #     analyzer = PSAAnalyzer

        self.analysis = analyzer(self.scenario, self.uuid)

    def manage(self):
        self.analysis.run()
