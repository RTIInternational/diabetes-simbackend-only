import os
import ast
import pandas as pd
import numpy as np
from shutil import rmtree, copyfile
from pathlib import Path

from src.configuration.configuration_manager import ConfigurationManager
from src.analysis.utils import unfurl_and_tally_events
from src.analysis import EVENTS

BASE_ANALYSIS_PATH = os.path.join('src', 'analysis', 'output')
BASE_POPULATION_PATH = os.path.join('src', 'population', 'output')
BASE_SIMULATION_PATH = os.path.join('src', 'simulation', 'output')
EXTENSIONS = ('.csv', '.pkl')


def rounder(num, ndigits=2):
    return round(float(num), ndigits)


class SimulationAnalyzer():
    def __init__(self, scenario, uuid):
        self.uuid = uuid
        self.scenario = scenario

    def _record_cost_effectiveness(self):
        """
        Generate content for the core output table
        """

        df = self.effectiveness_df

        def _get_run(group_label):
            parts = group_label.split('--')
            if len(parts) == 3:
                return parts[2]
            return parts[1]

        df['run'] = df['group'].map(_get_run)
        df_group_name = df['group']

        def _calculate_increments(df_group):
            row_data = {}
            non_intervention_cost = df_group.loc[df_group_name.str.contains('non'), 'total_cost'].values[0]
            non_intervention_health_cost = df_group.loc[df_group_name.str.contains('non'), 'total_health_cost'].values[
                0]
            non_intervention_event_cost = df_group.loc[df_group_name.str.contains('non'), 'total_event_cost'].values[0]
            non_intervention_intervention_cost = \
            df_group.loc[df_group_name.str.contains('non'), 'total_intervention_cost'].values[0]
            non_intervention_qualy = df_group.loc[df_group_name.str.contains('non'), 'qaly'].values[0]
            non_intervention_years = df_group.loc[df_group_name.str.contains('non'), 'remaining_life_years'].values[0]

            intervention_cost = df_group.loc[~df_group_name.str.contains('non'), 'total_cost'].values[0]
            intervention_health_cost = df_group.loc[~df_group_name.str.contains('non'), 'total_health_cost'].values[0]
            intervention_event_cost = df_group.loc[~df_group_name.str.contains('non'), 'total_event_cost'].values[0]
            intervention_intervention_cost = df_group.loc[~df_group_name.str.contains('non'), 'total_intervention_cost'].values[0]
            intervention_qualy = df_group.loc[~df_group_name.str.contains('non'), 'qaly'].values[0]
            intervention_years = df_group.loc[~df_group_name.str.contains('non'), 'remaining_life_years'].values[0]

            if self.scenario['diabetes_type'] == 'screen':
                intervention_screening_cost = df_group.loc[~df_group_name.str.contains('non'), 'total_screening_cost'].values[0]

            row_data['run'] = df_group.name
            population_size = self.scenario['size']
            row_data['Total cost non-intervention'] = round(non_intervention_cost / population_size, 2)
            row_data['QALY non-intervention'] = round(non_intervention_qualy / population_size, 4)
            row_data['Total cost intervention'] = round(intervention_cost / population_size, 2)
            row_data['QALY intervention'] = round(intervention_qualy / population_size, 4)
            cost_increment = (intervention_cost - non_intervention_cost) / population_size
            row_data['Cost increment'] = round(cost_increment, 2)
            qaly_incrememnt = (intervention_qualy - non_intervention_qualy) / population_size
            row_data['QALY increment'] = round(qaly_incrememnt, 4)

            if row_data['QALY increment']:
                icer = row_data['Cost increment'] / row_data['QALY increment']
                row_data['ICER'] = round(icer, 2)
            else:
                row_data['ICER'] = 0

            row_data['Remaining LY non-intervention'] = round(non_intervention_years / population_size, 4)
            row_data['Remaining LY intervention'] = round(intervention_years / population_size, 4)
            row_data['LY increment'] = round((intervention_years - non_intervention_years) / population_size, 4)

            row_data['Treatment costs - non-intervention'] = round(non_intervention_health_cost / population_size, 2)
            row_data['Complication costs - non-intervention'] = round(non_intervention_event_cost / population_size, 2)
            row_data['Intervention costs - non-intervention'] = round(non_intervention_intervention_cost / population_size, 2)
            row_data['Treatment costs - intervention'] = round(intervention_health_cost / population_size, 2)
            row_data['Complication costs - intervention'] = round(intervention_event_cost / population_size, 2)
            row_data['Intervention costs - intervention'] = round(intervention_intervention_cost / population_size, 2)

            if self.scenario['diabetes_type'] == 'screen':
                row_data['Screening costs - non-intervention'] = 0
                row_data['Screening costs - intervention'] = round(intervention_screening_cost / population_size, 2)

            return row_data

        ce_data = [x for x in df.groupby('run').apply(_calculate_increments)]
        ce_df = pd.DataFrame(ce_data)
        ce_t_df = ce_df.T

        mean_df = pd.DataFrame(ce_df.mean().round(4))
        mean_df_T = mean_df.T
        mean_df_T = mean_df_T.drop(columns=['run'])
        alt_icer_name = 'ICER: mean inc Cost / mean inc QALY'
        if mean_df_T['QALY increment'].values[0]:
            alt_icer = mean_df_T['Cost increment'] / mean_df_T['QALY increment']
        else:
            alt_icer = 0

        mean_df_T[alt_icer_name] = round(alt_icer, 4)
        mean_df_T.to_csv(os.path.join(self.analysis_path, 'mean cost_effectiveness.csv'), index=False)

        columns = []
        for i in range(1, len(ce_df) + 1):
            columns.append(f'run {i}')
        ce_t_df.columns = columns
        ce_t_df.drop(['run'], axis=0, inplace=True)

        # add mean row to core summary output; since mean is a row added to a DF with rows for each iteration
        # "run" (= iteration number) is set to "mean";
        mean_df_T['run'] = 'mean'
        ce_df = pd.concat([ce_df, mean_df_T])
        # alt_icer is calculated separately (all other values are automatically averaged) so make sure only the mean
        # row has a value
        ce_df[alt_icer_name] = [mean_df_T[alt_icer_name].values[0] if 'mean' in x else np.nan for x in ce_df['run']]

        ordered_columns = ['run', 'Total cost non-intervention', 'Treatment costs - non-intervention',
                           'Complication costs - non-intervention', 'Intervention costs - non-intervention',
                           'QALY non-intervention', 'Total cost intervention', 'Treatment costs - intervention',
                           'Complication costs - intervention', 'Intervention costs - intervention',
                           'QALY intervention', 'Cost increment', 'QALY increment', 'ICER',
                           'ICER: mean inc Cost / mean inc QALY', 'Remaining LY non-intervention',
                           'Remaining LY intervention', 'LY increment']
        if self.scenario['diabetes_type'] == 'screen':
            ordered_columns = ['run', 'Total cost non-intervention', 'Treatment costs - non-intervention',
                               'Complication costs - non-intervention', 'Intervention costs - non-intervention',
                               'Screening costs - non-intervention',
                               'QALY non-intervention', 'Total cost intervention', 'Treatment costs - intervention',
                               'Complication costs - intervention', 'Intervention costs - intervention',
                               'Screening costs - intervention',
                               'QALY intervention', 'Cost increment', 'QALY increment', 'ICER',
                               'ICER: mean inc Cost / mean inc QALY', 'Remaining LY non-intervention',
                               'Remaining LY intervention', 'LY increment']

        ce_df = ce_df[ordered_columns]
        ce_file = os.path.join(self.analysis_path, 'cost_effectiveness.csv')
        ce_file_t = os.path.join(self.analysis_path, 'cost_effectiveness transposed.csv')
        ce_df.to_csv(ce_file, index=False)
        ce_t_df.to_csv(ce_file_t, index=False)

    def _record_yearly_cost_effectiveness(self):
        """
        Generate a chart of cost effectiveness
        """

        df = self.yearly_effectiveness_df

        def _get_run(group_label):
            parts = group_label.split('--')
            if len(parts) == 3:
                return parts[2]
            return parts[1]

        df['run'] = df['group'].map(_get_run)
        df_group_name = df['group']

        def _calculate_increments(df_group):
            row_data = {}
            unique_group_names = df_group['group'].unique()
            group_names = [x.split('--')[0] for x in unique_group_names]
            intervention_cost = 0
            intervention_qaly = 0
            non_intervention_cost = 0
            non_intervention_qaly = 0
            intervention_cost_cumulative = 0
            intervention_qaly_cumulative = 0
            non_intervention_cost_cumulative = 0
            non_intervention_qaly_cumulative = 0
            if 'non-intervention' in group_names:
                non_intervention_cost = df_group.loc[df_group_name.str.contains('non'), 'overall_cost'].values[0]
                non_intervention_qaly = df_group.loc[df_group_name.str.contains('non'), 'qaly'].values[0]
                non_intervention_cost_cumulative = df_group.loc[df_group_name.str.contains('non'), 'cumulative health cost'].values[0]
                non_intervention_qaly_cumulative = df_group.loc[df_group_name.str.contains('non'), 'cumulative qaly'].values[0]

            if 'intervention' in group_names:
                intervention_cost = df_group.loc[~df_group_name.str.contains('non'), 'overall_cost'].values[0]
                intervention_qaly = df_group.loc[~df_group_name.str.contains('non'), 'qaly'].values[0]
                intervention_cost_cumulative = \
                df_group.loc[~df_group_name.str.contains('non'), 'cumulative health cost'].values[0]
                intervention_qaly_cumulative = \
                df_group.loc[~df_group_name.str.contains('non'), 'cumulative qaly'].values[0]

            row_data['run'] = df_group.name[0]
            row_data['year'] = df_group.name[1]

            population_size = self.scenario['size']

            row_data['intervention_cost_cumulative'] = intervention_cost_cumulative
            row_data['non_intervention_cost_cumulative'] = non_intervention_cost_cumulative
            row_data['intervention_qaly_cumulative'] = intervention_qaly_cumulative
            row_data['non_intervention_qaly_cumulative'] = non_intervention_qaly_cumulative

            row_data['cost_non_intervention_by_person'] = round(non_intervention_cost, 2) / population_size
            row_data['qaly_non_intervention_by_person'] = round(non_intervention_qaly, 4) / population_size
            row_data['cost_intervention_by_person'] = round(intervention_cost, 2) / population_size
            row_data['qaly_intervention_by_person'] = round(intervention_qaly, 4) / population_size
            row_data['cost_increment_by_person'] = (intervention_cost - non_intervention_cost) / population_size
            row_data['qaly_increment_by_person'] = (intervention_qaly - non_intervention_qaly) / population_size

            row_data['cumulative cost_non_intervention_by_person'] = round(non_intervention_cost_cumulative,
                                                                           2) / population_size
            row_data['cumulative qaly_non_intervention_by_person'] = round(non_intervention_qaly_cumulative,
                                                                           4) / population_size
            row_data['cumulative cost_intervention_by_person'] = round(intervention_cost_cumulative,
                                                                       2) / population_size
            row_data['cumulative qaly_intervention_by_person'] = round(intervention_qaly_cumulative,
                                                                       4) / population_size

            row_data['cumulative cost_increment_by_person'] = (intervention_cost_cumulative - non_intervention_cost_cumulative) / population_size
            row_data['cumulative qaly_increment_by_person'] = (intervention_qaly_cumulative - non_intervention_qaly_cumulative) / population_size

            return row_data

        ce_data = [x for x in df.groupby(['run', 'step']).apply(_calculate_increments)]
        ce_df = pd.DataFrame(ce_data)

        # fixes cumulative increment issue where non-intervention and intervention
        # could run for a different number of time steps
        zero_indeces = []
        if 0 in ce_df['cumulative cost_intervention_by_person'].values:
            zero_indeces = ce_df[ce_df['cumulative cost_intervention_by_person'] == 0].index
            first_0_index = zero_indeces[0]
            last_value = ce_df['cumulative cost_intervention_by_person'].iloc[first_0_index - 1]
            for i in zero_indeces:
                ce_df['cumulative cost_intervention_by_person'].iloc[i] = last_value
        if 0 in ce_df['cumulative cost_non_intervention_by_person'].values:
            zero_indeces = ce_df[ce_df['cumulative cost_non_intervention_by_person'] == 0].index
            first_0_index = zero_indeces[0]
            last_value = ce_df['cumulative cost_non_intervention_by_person'].iloc[first_0_index - 1]
            for i in zero_indeces:
                ce_df['cumulative cost_non_intervention_by_person'].iloc[i] = last_value
        for i in zero_indeces:
            ce_df['cumulative cost_increment_by_person'].iloc[i] = \
                ce_df['cumulative cost_intervention_by_person'].iloc[i] - \
                ce_df['cumulative cost_non_intervention_by_person'].iloc[i]

        qaly_zero_indeces = []
        if 0 in ce_df['cumulative qaly_intervention_by_person'].values:
            qaly_zero_indeces = ce_df[ce_df['cumulative qaly_intervention_by_person'] == 0].index
            qaly_first_0_index = zero_indeces[0]
            qaly_last_value = ce_df['cumulative qaly_intervention_by_person'].iloc[qaly_first_0_index - 1]
            for i in qaly_zero_indeces:
                ce_df['cumulative qaly_intervention_by_person'].iloc[i] = qaly_last_value
        if 0 in ce_df['cumulative qaly_non_intervention_by_person'].values:
            qaly_zero_indeces = ce_df[ce_df['cumulative qaly_non_intervention_by_person'] == 0].index
            qaly_first_0_index = qaly_zero_indeces[0]
            qaly_last_value = ce_df['cumulative qaly_non_intervention_by_person'].iloc[qaly_first_0_index - 1]
            for i in qaly_zero_indeces:
                ce_df['cumulative qaly_non_intervention_by_person'].iloc[i] = qaly_last_value
        for i in qaly_zero_indeces:
            ce_df['cumulative qaly_increment_by_person'].iloc[i] = \
                ce_df['cumulative qaly_intervention_by_person'].iloc[i] - \
                ce_df['cumulative qaly_non_intervention_by_person'].iloc[i]

        def _calculate_icer(row):
            cost_increment = row['cumulative cost_increment_by_person']
            qaly_increment = row['cumulative qaly_increment_by_person']
            if qaly_increment:
                return rounder(cost_increment / qaly_increment)
            else:
                return 0

        ce_df['icer'] = ce_df.apply(_calculate_icer, axis=1)

        per_person_column_order = [
            'run', 'year', 'cumulative cost_non_intervention_by_person',
            'cumulative cost_intervention_by_person', 'cumulative cost_increment_by_person',
            'cumulative qaly_non_intervention_by_person', 'cumulative qaly_intervention_by_person',
            'cumulative qaly_increment_by_person', 'icer'
        ]

        per_person_file = os.path.join(self.analysis_path, 'per_person_cost_effectiveness.csv')
        per_person_file_T = os.path.join(self.analysis_path, 'per_person_effectiveness transposed.csv')

        per_person_df = ce_df[per_person_column_order]
        per_person_df.to_csv(per_person_file, index=False)

        # avoid "run" and "year" columns
        per_person_df_T = per_person_df.iloc[:, 2:].T
        iterations = self.scenario['iterations']
        if self.scenario['time_horizon'] == 'max_steps':
            years_dict = {i: self.scenario['iterations'] for i in range(1, iterations + 1)}
        else:
            years_dict = per_person_df.groupby('run').size().to_dict()

        columns = []
        for run, years in years_dict.items():
            for year in range(1, years + 1):
                columns.append(f'run: {int(run)} - year: {year}')

        per_person_df_T.columns = columns
        per_person_df_T.to_csv(per_person_file_T, index=False)

    def _record_incidence(self):
        """
        Generate a chart of event counts
        """
        cumulative_csv_file = os.path.join(self.analysis_path, 'cumulative incidence.csv')
        indiv_csv_file = os.path.join(self.analysis_path, 'incidence.csv')

        _df = self.incidence_df.drop(['person_years'], axis=1)
        cumulative_columns = [x for x in _df.columns if 'cumulative' in x]
        cumulative_columns.append('count_surviving')
        indiv_columns = [x for x in _df.columns if 'cumulative' not in x]
        indiv_columns = [x for x in indiv_columns if x not in ['group', 'step']]

        df = _df.set_index(['group', 'step'])
        df.sort_index(axis=1, inplace=True)

        cumulative_df = df[cumulative_columns]
        cumulative_df.columns = [x.replace('cumulative ', '') for x in cumulative_columns]
        cumulative_df.to_csv(cumulative_csv_file)
        df[indiv_columns].to_csv(indiv_csv_file)

    def _record_prevalence(self):
        """
        Generate a table with total counts (prevalence) for all events
        """

        def _do(group):
            aggregate = {'group': group.name}
            for event in self.events:
                aggregate[event] = group[event].sum()
            aggregate['person_years'] = int(group['person_years'].mean())
            aggregate['intervention'] = group['intervention'].values[0]
            return aggregate

        event_data = [x for x in self.incidence_df.groupby('group').apply(_do)]
        event_df = pd.DataFrame(event_data)
        event_df.set_index(['group'], inplace=True)
        event_df.sort_index(axis=1, inplace=True)
        event_df.to_csv(os.path.join(self.analysis_path, 'prevalence.csv'))

        mean_event_df = event_df.groupby('intervention').mean()
        mean_event_df.to_csv(os.path.join(self.analysis_path, 'mean_prevalence.csv'))

    def _combine(self, datasets):
        self.effectiveness_df = datasets['effectiveness']
        self.yearly_effectiveness_df = datasets['yearly_effectiveness']
        self.incidence_df = datasets['incidence']

    def _collapse(self):
        """
        For each CSV generated by the simulation, total the results for a few
        specific metrics.

        :returns: collapsed dataframe
        """
        effectiveness_data = []
        yearly_effectiveness_data = []
        incidence_data = []

        data_filepath = os.path.join(self.analysis_path, 'data')
        for filename in os.listdir(data_filepath):
            # UI simulations generate a UUID for each simulation. This UUID is
            # used to gather results after completion. While we're confident
            # the UUID won't collide in UI simulations, we can't say the same
            # for CLI. CLI assigns a synthetic UUID of "CLI". As you can imagine,
            # this will absolutely collide. The following conditional ensures
            # only CSV files belonging to the scenario at hand are processed.
            if (not filename.endswith(EXTENSIONS) or
                    not filename.startswith(self.scenario['scenario_name'])):
                continue

            # Split the filename on its delimiter and stash its parts
            scenario_name, run_type = self._unpack_filename(filename)
            # df = pd.read_csv(os.path.join(data_filepath, filename))
            df = pd.read_pickle(os.path.join(data_filepath, filename))
            intervention = 0 if 'non-intervention' in run_type else 1
            data = self._set_data(df, run_type, intervention)

            effectiveness_data.append(data['effectiveness'])
            yearly_effectiveness_data.append(data['yearly_effectiveness'])
            incidence_data.append(data['incidence'])

        effectiveness = pd.concat(effectiveness_data, ignore_index=True)
        yearly_effectiveness = pd.concat(yearly_effectiveness_data, ignore_index=True)
        incidence = pd.concat(incidence_data, ignore_index=True)

        return {
            'effectiveness': effectiveness,
            'yearly_effectiveness': yearly_effectiveness,
            'incidence': incidence
        }

    def _consolidate_data(self):
        """
        Consolidate the data files from each simulation run in a single directory.
        """
        if not os.path.exists(os.path.join(self.analysis_path, 'data')):
            os.mkdir(os.path.join(self.analysis_path, 'data'))

        # For every csv or pkl in the simulation directory, copy its content to the
        # corresponding analysis directory.
        for filename in os.listdir(self.simulation_path):
            if not filename.endswith(EXTENSIONS):
                continue

            src_path = os.path.join(self.simulation_path, filename)
            dest_path = os.path.join(self.analysis_path, 'data', filename)
            copyfile(src_path, dest_path)

    def _copy_scenario(self):
        """
        Write the scenario file into the analysis directory
        """
        config = ConfigurationManager(self.scenario)
        config.write(self.analysis_path, 'scenario')

    def _purge_simulation_directories(self):
        # Purge the sim and pop directories
        for path in Path(self.population_path).glob('**/*'):
            if path.is_file():
                path.unlink()
        # rmtree(self.population_path)
        rmtree(self.simulation_path)
        rmtree(self.analysis_raw_data_path)

    def _set_cost_effectiveness(self, df, group, is_intervention):
        """
        Compute the total cost effectiveness

        :param df: DataFrame to plot
        :param group: Stratified group (or None)
        """
        df['total_cost'] = df['overall_cost'].map(lambda hc: sum(hc))
        df['total_health_cost'] = df['health_cost'].map(lambda hc: sum(hc))
        df['total_event_cost'] = df['event_cost'].map(lambda hc: sum(hc))
        df['total_intervention_cost'] = df['intervention_cost'].map(lambda hc: sum(hc))
        df['qaly_value'] = df['qaly'].map(lambda q: sum(q))
        if self.scenario['diabetes_type'] in ['pre', 'screen']:
            df['remaining_life_years'] = df['age'] - df['age_entry_fixed']
        else:
            df['remaining_life_years'] = df['age'] - df['age_entry']

        cost = round(df['total_cost'].sum(), 2)
        health_cost = round(df['total_health_cost'].sum(), 2)
        event_cost = round(df['total_event_cost'].sum(), 2)
        intervention_cost = round(df['total_intervention_cost'].sum(), 2)

        qaly = round(df['qaly_value'].sum(), 4)
        life_years = round(df['remaining_life_years'].sum(), 2)

        cost_effectiveness_dict = {
            'group': group,
            'intervention': is_intervention,
            'total_cost': cost,
            'total_health_cost': health_cost,
            'total_event_cost': event_cost,
            'total_intervention_cost': intervention_cost,
            'qaly': qaly,
            'remaining_life_years': life_years
        }

        if self.scenario['diabetes_type'] == 'screen':
            df['total_screening_cost'] = df['total_screening_cost'].map(lambda hc: sum(hc))
            screening_cost = round(df['total_screening_cost'].sum(), 2)
            cost_effectiveness_dict['total_screening_cost'] = screening_cost

        ce_df = pd.DataFrame.from_dict([cost_effectiveness_dict])

        return ce_df

    def _set_yearly_cost_effectiveness(self, df, group, is_intervention):
        aggregate = pd.DataFrame()

        for event in ['overall_cost', 'qaly']:
            aggregate = aggregate.join(unfurl_and_tally_events(df, event), how="right")

        aggregate['cumulative health cost'] = aggregate['overall_cost'].cumsum()
        aggregate['cumulative qaly'] = aggregate['qaly'].cumsum()
        aggregate['step'] = [i + 1 for i in range(len(aggregate))]
        aggregate['group'] = group
        aggregate['intervention'] = is_intervention

        return aggregate

    def _set_data(self, raw_data, group, is_intervention):
        """
        Set the instance data object.

        :param data: Data file name
        """

        def _eval(elem):
            """
            Use ast.literal_eval to unpack string representations of lists. We
            use lists in the simulation in order to maintain a historical record
            of changes. When this is saved to disc, the lists are converted to
            strings.

            :param elem: Element of the dataframe to evaluate
            :returns: eval'd element
            """
            try:
                return ast.literal_eval(elem)
            except ValueError:
                # Floats are not eval'd by ast.literal_eval, so we have to catch
                # ValueErrors. Return them directly.
                # https://docs.python.org/3.6/library/ast.html#ast.literal_eval
                return elem

        clean_data = raw_data.applymap(_eval)
        incidence = self._set_incidence(clean_data, group, is_intervention)
        effectiveness_by_year = self._set_yearly_cost_effectiveness(clean_data, group, is_intervention)
        effectiveness = self._set_cost_effectiveness(clean_data, group, is_intervention)

        return {
            'effectiveness': effectiveness,
            'yearly_effectiveness': effectiveness_by_year,
            'incidence': incidence
        }

    def _set_events(self):
        self.events = EVENTS[self.equation_set]

    def _set_incidence(self, df, group, is_intervention):
        population_size = len(df)

        aggregate = pd.DataFrame()
        for event in self.events:
            aggregate = aggregate.join(unfurl_and_tally_events(df, event), how="right")
            aggregate[f'cumulative {event}'] = aggregate[event].cumsum()

        aggregate['step'] = [i + 1 for i in range(len(aggregate))]
        aggregate['group'] = group
        aggregate['intervention'] = is_intervention
        aggregate['person_years'] = df['lifespan'].sum()

        aggregate['count_surviving'] = [population_size - deaths for deaths in aggregate['cumulative death']]

        return aggregate

    def _set_output_directories(self):
        """
        Generate UUID based output directories for population generation and
        simulation tasks.
        """
        self.analysis_path = os.path.join(BASE_ANALYSIS_PATH, self.uuid)
        self.population_path = os.path.join(BASE_POPULATION_PATH, self.uuid)
        self.simulation_path = os.path.join(BASE_SIMULATION_PATH, self.uuid)
        self.analysis_raw_data_path = os.path.join(BASE_ANALYSIS_PATH, self.uuid, 'data')

    def _set_scenario(self):
        """
        Set the analysis scenario

        :param scenario: Scenario file to parse
        """
        economics = {}

        self.scenario_name = self.scenario['scenario_name']
        self.equation_set = self.scenario['diabetes_type']

        intervention_cost = 0
        if 'intervention_cost' in economics:
            intervention_cost = economics['intervention_cost']

        self.intervention_cost = intervention_cost

    def _unpack_filename(self, filename):
        """
        Given a filename delimited by '__', split it into corresponding pieces.

        :param filename: delimited filename ([scenario name]__[baseline|intervention])
        :returns: list of [scenario name, baseline|intervention]
        """
        # return filename.replace(".csv", "").split("__")
        return filename.replace(".pkl", "").split("__")

    def setup(self):
        """
        Get ready for an analysis.
        """
        self._set_scenario()
        self._set_output_directories()
        self._set_events()
        self._consolidate_data()
        self._copy_scenario()

    def fix_non_compliers(self):
        # non-complying individual in an intervention run will be replaced by corresponding individuals
        # from the associated non-intervention run; per instructions of the PI

        data_filepath = os.path.join(self.analysis_path, 'data')

        for i in range(1, self.scenario['iterations'] + 1):
            df_dict = {}
            padded_i = str(i).rjust(4, '0')
            for filename in os.listdir(data_filepath):
                if (not filename.endswith(EXTENSIONS) or
                        not filename.startswith(self.scenario['scenario_name'])):
                    continue
                if padded_i in filename:
                    # df = pd.read_csv(os.path.join(data_filepath, filename))
                    df = pd.read_pickle(os.path.join(data_filepath, filename))
                    run_type = filename.split('__')[1].split('--')[0]
                    df_dict[run_type] = df
            intervention_df = df_dict['intervention']
            intervention_df.to_csv(os.path.join(data_filepath, 'intervention_source.csv'), index=False)
            interventions = ['glycemic', 'cholesterol', 'bp', 'lifestyle']
            all_non_complying_rows = []
            for intervention in interventions:
                if f'{intervention}_non_compliant' in intervention_df.columns:
                    non_complier_rows = intervention_df.index[
                        intervention_df[f'{intervention}_non_compliant'] == 1].tolist()
                    all_non_complying_rows += non_complier_rows
            non_intervention_df = df_dict['non-intervention']
            intervention_df.loc[all_non_complying_rows] = non_intervention_df.loc[all_non_complying_rows]
            intervention_df.to_csv(os.path.join(data_filepath, 'intervention_replaced.csv'), index=False)
            non_intervention_df.to_csv(os.path.join(data_filepath, 'non-intervention-source.csv'), index=False)

    def build(self):
        """
        This is essentially a map/reduce, cutting n files into two dataframes.
        """
        self._combine(self._collapse())

    def plot(self):
        """
        Create tables from the data.
        """
        self._record_incidence()
        self._record_prevalence()
        self._record_cost_effectiveness()
        self._record_yearly_cost_effectiveness()

    def cleanup(self):
        """
        Perform any necessary teardown steps.
        """
        # Purge the sim and pop directories
        for path in Path(self.population_path).glob('**/*'):
            if path.is_file():
                path.unlink()
        # if a user wants to save a population data set this directory must not be purged
        if not self.scenario['save_items_on_run'][0]['save_population']:
            rmtree(self.population_path)
        rmtree(self.simulation_path)
        rmtree(self.analysis_raw_data_path)

    def run(self):
        """
        Run the analysis pipeline.
        """
        self.setup()
        self.fix_non_compliers()
        self.build()
        self.plot()
        self.cleanup()
