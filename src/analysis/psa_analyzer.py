import pandas as pd
import os
from src.analysis.simulation_analyzer import SimulationAnalyzer
from statistics import mean

CEILING_RATIOS = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,
                  12000, 14000, 16000, 18000, 20000, 22000, 24000, 26000, 28000,
                  30000, 35000, 40000, 45000, 50000, 60000, 70000, 80000, 90000,
                  100000, 125000, 150000, 175000, 200000, 225000, 250000, 275000,
                  300000, 325000, 350000, 375000, 400000, 425000, 450000, 500000]


class PSAAnalyzer(SimulationAnalyzer):

    def _calculate_ce(self):
        """
        Quantify cost effectiveness via a Cost Effectiveness Acceptability Curve (CEAC)

        Not currently used for analysis
        """
        df = self.ce_df
        ceas = []
        for cr in CEILING_RATIOS:
            intervention_effectiveness = []

            def _is_effective(row):
                """
                Per economist: "The CEAC is basically formed by evaluating the
                equation: Incremental cost – (WTP)*(Incremental QALY)

                If the equation is >0, that favors the baseline;
                if it is <0, it favors the intervention."
                """
                intervention_effectiveness.append(int(row['cost_increment'] - (cr * row['qaly_increment']) < 0))

            df.apply(_is_effective, axis=1)

            intervention_ce = mean(intervention_effectiveness)
            base_ce = 1 - intervention_ce

            ceas.append({
                'cratio': round(float(cr), 2),
                'non_intervention': round(float(base_ce), 2),
                'intervention': round(float(intervention_ce), 2)
            })

        df = pd.DataFrame(ceas)

        cefile = os.path.join(self.analysis_path, 'cea.csv')
        df.to_csv(cefile, index=False)

    def plot(self):
        """
        Create tables from the data.
        """
        self._record_prevalence()
        self._record_cost_effectiveness()
        self._calculate_ce()
