import argparse
import pandas as pd
import os
import copy

INPUT_DIR = os.path.join('data', 'raw')
OUTPUT_DIR = os.path.join('data')


def process_lookahead_accord():
    column_rename = {
        'ID': 'seqn', 'AGE': 'age_entry', 'DUR_YR00': 'diabetes_duration_entry',
        'EDUCOLL': 'has_postsecondary_ed', 'OBSEXREC': 'female',
        'BLACK': 'black', 'HISPANIC': 'hispanic', 'OTHER_RACE': 'other_race'
    }

    raw_population_df = pd.read_csv(os.path.join(INPUT_DIR, 't2d_lookahead_accord.csv'))
    raw_population_df.rename(columns=column_rename, inplace=True)
    raw_population_df['diabetes_duration_entry'].fillna(0, inplace=True)

    def apply(row):
        new_row = copy.deepcopy(row)
        new_row['age'] = int(row['age_entry'])
        new_row['bmi'] = "[{}]".format(row['FBMI'])
        new_row['sbp'] = "[{}]".format(row['FBPS'])
        new_row['hba1c'] = "[{}]".format(row['FHBA1C'])
        new_row['hdl'] = "[{}]".format(row['FHDL'])
        new_row['ldl'] = "[{}]".format(row['FLDL'])
        new_row['smoker'] = "[{}]".format(int(row['FSMOKES']))
        new_row['serum_creatinine'] = "[{}]".format(row['FSCREAT'])
        new_row['trig'] = "[{}]".format(row['LN_FTRG'])

        new_row['la_trial_first_year'] = int(row['LA_TRIAL_FIRST_YEAR'])
        new_row['intensive_la_treatment'] = int(row['INTENSIVE_LA_TX'])
        new_row['intensive_la_treatment_first_year'] = int(row['INTENSIVE_LA_TX_FIRST_YEAR'])
        new_row['hba1c_treatment_first_year'] = int(row['FHBA1C_TX_FIRST_YEAR'])
        new_row['hba1c_treatment'] = int(row['FHBA1C_TX'])
        new_row['sbp_treatment_first_year'] = int(row['FBPS_TX_FIRST_YEAR'])
        new_row['sbp_treatment'] = int(row['FBPS_TX'])
        new_row['hdl_treatment_first_year'] = int(row['FHDL_TX_FIRST_YEAR'])
        new_row['hdl_treatment'] = int(row['FHDL_TX'])
        new_row['ldl_treatment_first_year'] = int(row['FLDL_TX_FIRST_YEAR'])
        new_row['ldl_treatment'] = int(row['FLDL_TX'])
        new_row['trig_treatment_first_year'] = int(row['FTRG_TX_FIRST_YEAR'])
        new_row['trig_treatment'] = int(row['FTRG_TX'])
        new_row['serum_creatinine_treatment_first_year'] = int(row['FSCREAT_TX_FIRST_YEAR'])
        new_row['serum_creatinine_treatment'] = int(row['FSCREAT_TX'])
        new_row['smoker_treatment'] = int(row['FSMOKES_TX'])

        new_row['amputation'] = "[{}]".format(int(row['AMP_HIST']))
        new_row['macroalbuminuria'] = "[{}]".format(int(row['MACRO_HIST']))
        new_row['microalbuminuria'] = "[{}]".format(int(row['MICRO_HIST']))
        new_row['blindness'] = "[{}]".format(int(row['BLINDNESS_HIST']))
        new_row['ulcer'] = "[{}]".format(int(row['FTULCER_HIST']))
        new_row['mi'] = "[{}]".format(int(row['MI_HIST']))
        new_row['stroke'] = "[{}]".format(int(row['STROKE_HIST']))
        new_row['chf'] = "[{}]".format(int(row['CHF_HIST']))
        new_row['angina'] = "[{}]".format(int(row['ANGINA_HIST']))
        new_row['dialysis'] = "[{}]".format(int(row['DIALYSIS_HIST']))
        new_row['egfr_60'] = "[{}]".format(int(row['EGFR60_HIST']))
        new_row['egfr_30'] = "[{}]".format(int(row['EGFR30_HIST']))
        new_row['revasc'] = "[{}]".format(int(row['REVASC_HIST']))
        new_row['neurop'] = "[{}]".format(int(row['NEUROP_HIST']))
        new_row['laser_retina'] = "[{}]".format(int(row['LASER_HIST']))

        new_row['la_trial'] = int(row['LA_TRIAL'])

        if row['ACCORD']:
            new_row['dataset'] = 'accord'
            new_row['accord'] = 1
        else:
            new_row['dataset'] = 'lookahead'
            new_row['accord'] = 0

        return new_row

    converted_df = raw_population_df.apply(apply, axis=1)

    drop_cols = ['LA_TRIAL', 'ACCORD', 'LA_TRIAL_FIRST_YEAR', 'INTENSIVE_LA_TX',
                 'INTENSIVE_LA_TX_FIRST_YEAR', 'FHBA1C_TX', 'FBPS_TX', 'FHDL_TX',
                 'FLDL_TX', 'FSCREAT_TX', 'FSMOKES_TX',
                 'FHBA1C_TX_FIRST_YEAR', 'FBPS_TX_FIRST_YEAR', 'FHDL_TX_FIRST_YEAR',
                 'FLDL_TX_FIRST_YEAR', 'FTRG_TX_FIRST_YEAR', 'FSCREAT_TX_FIRST_YEAR',
                 'MI_HIST', 'STROKE_HIST', 'CHF_HIST', 'ANGINA_HIST', 'DIALYSIS_HIST',
                 'EGFR60_HIST', 'EGFR30_HIST', 'REVASC_HIST',
                 'BLINDNESS_HIST', 'NEUROP_HIST', 'LASER_HIST', 'AMP_HIST',
                 'MICRO_HIST', 'MACRO_HIST', 'FHBA1C', 'FBMI', 'FBPS', 'FHDL',
                 'FLDL', 'LN_FTRG', 'FSCREAT', 'FSMOKES', 'YEAR']

    converted_df.drop(drop_cols, axis=1, inplace=True)
    converted_df.drop(converted_df.columns[converted_df.columns.str.contains('unnamed',
                                                                             case=False)],
                      axis=1, inplace=True)

    converted_df['lifespan'] = 0
    converted_df['should_update'] = 1
    converted_df['deceased'] = 0

    converted_df["current_cvd_death"] = "[0]"
    converted_df["ever_cvd_death"] = "[0]"
    converted_df["non_cvd_death"] = "[0]"
    converted_df["death"] = "[0]"
    converted_df["qaly"] = "[1]"
    converted_df["health_cost"] = "[0]"
    converted_df['hypoglycemia_medical'] = "[0]"
    converted_df['hypoglycemia_any'] = "[0]"
    converted_df['dialysis'] = "[0]"

    converted_df['quit_smoking'] = "[0]"
    converted_df['glycemic drug'] = "[0]"
    converted_df['bp drug'] = "[0]"
    converted_df['statin type'] = "[0]"
    converted_df[f'smoking intervention'] = "[0]"

    def get_cvd(row):
        if (
            row['mi'] == '[1]' or
            row['chf'] == '[1]' or
            row['stroke'] == '[1]' or
            row['revasc'] == '[1]' or
            row['angina'] == '[1]'
        ):
            return "[1]"
        return "[0]"

    converted_df['cvd'] = converted_df.apply(lambda x: get_cvd(x), axis=1)

    converted_df.to_csv(os.path.join(OUTPUT_DIR, 't2d_lookahead_accord.csv'), index=False)
    converted_df[converted_df['accord'] == 0].to_csv(os.path.join(OUTPUT_DIR, 't2d_lookahead.csv'), index=False)
    converted_df[converted_df['accord'] == 1].to_csv(os.path.join(OUTPUT_DIR, 't2d_accord.csv'), index=False)


def process_nhanes():
    column_rename = {
        'ID': 'seqn', 'AGE': 'age_entry', 'DUR_YR00': 'diabetes_duration_entry',
        'EDUCOLL': 'has_postsecondary_ed', 'OBSEXREC': 'female',
        'BLACK': 'black', 'HISPANIC': 'hispanic', 'OTHER_RACE': 'other_race'
    }

    raw_population_df = pd.read_csv(os.path.join(INPUT_DIR, 't2d_nhanes.csv'))
    raw_population_df.rename(columns=column_rename, inplace=True)

    def apply(row):
        new_row = copy.deepcopy(row)
        new_row['age'] = int(row['age_entry'])
        new_row['bmi'] = "[{}]".format(row['FBMI'])
        new_row['sbp'] = "[{}]".format(row['FBPS'])
        new_row['hba1c'] = "[{}]".format(row['FHBA1C'])
        new_row['hdl'] = "[{}]".format(row['FHDL'])
        new_row['ldl'] = "[{}]".format(row['FLDL'])
        new_row['smoker'] = "[{}]".format(row['FSMOKES'])
        new_row['serum_creatinine'] = "[{}]".format(row['FSCREAT'])
        new_row['trig'] = "[{}]".format(row['LN_FTRG'])

        new_row['la_trial_first_year'] = int(row['LA_TRIAL_FIRST_YEAR'])
        new_row['intensive_la_treatment'] = int(row['INTENSIVE_LA_TX'])
        new_row['intensive_la_treatment_first_year'] = int(row['INTENSIVE_LA_TX_FIRST_YEAR'])
        new_row['hba1c_treatment_first_year'] = int(row['FHBA1C_TX_FIRST_YEAR'])
        new_row['hba1c_treatment'] = int(row['FHBA1C_TX'])
        new_row['sbp_treatment_first_year'] = int(row['FBPS_TX_FIRST_YEAR'])
        new_row['sbp_treatment'] = int(row['FBPS_TX'])
        new_row['hdl_treatment_first_year'] = int(row['FHDL_TX_FIRST_YEAR'])
        new_row['hdl_treatment'] = int(row['FHDL_TX'])
        new_row['ldl_treatment_first_year'] = int(row['FLDL_TX_FIRST_YEAR'])
        new_row['ldl_treatment'] = int(row['FLDL_TX'])
        new_row['trig_treatment_first_year'] = int(row['FTRG_TX_FIRST_YEAR'])
        new_row['trig_treatment'] = int(row['LN_FTRG_TX'])
        new_row['serum_creatinine_treatment_first_year'] = int(row['FSCREAT_TX_FIRST_YEAR'])
        new_row['serum_creatinine_treatment'] = int(row['FSCREAT_TX'])
        new_row['smoker_treatment'] = int(row['FSMOKES_TX'])

        new_row['amputation'] = "[{}]".format(row['AMP_HIST'])
        new_row['macroalbuminuria'] = "[{}]".format(row['MACRO_HIST'])
        new_row['microalbuminuria'] = "[{}]".format(row['MICRO_HIST'])
        new_row['blindness'] = "[{}]".format(row['BLINDNESS_HIST'])
        new_row['ulcer'] = "[{}]".format(row['FOOT_ULCER_HIST'])
        new_row['mi'] = "[{}]".format(row['MI_HIST'])
        new_row['stroke'] = "[{}]".format(row['STROKE_HIST'])
        new_row['chf'] = "[{}]".format(row['CHF_HIST'])
        new_row['angina'] = "[{}]".format(row['ANGINA_HIST'])
        new_row['dialysis'] = "[{}]".format(row['DIALYSIS_HIST'])
        new_row['egfr_60'] = "[{}]".format(row['EGFR_60_HIST'])
        new_row['egfr_30'] = "[{}]".format(row['EGFR_30_HIST'])
        new_row['revasc'] = "[{}]".format(row['REVASC_HIST'])
        new_row['neurop'] = "[{}]".format(row['NEUROP_HIST'])
        new_row['laser_retina'] = "[{}]".format(row['LASER_HIST'])

        new_row['la_trial'] = int(row['LA_TRIAL'])

        if row['ACCORD']:
            new_row['dataset'] = 'accord'
        else:
            new_row['dataset'] = 'lookahead'

        return new_row

    converted_df = raw_population_df.apply(apply, axis=1)

    DROP_COLS = ['YEAR', 'LA_TRIAL', 'ACCORD',  'LA_TRIAL_FIRST_YEAR',
                 'INTENSIVE_LA_TX', 'INTENSIVE_LA_TX_FIRST_YEAR', 'FHBA1C_TX',
                 'FBPS_TX', 'FHDL_TX', 'FLDL_TX', 'LN_FTRG_TX', 'FSCREAT_TX',
                 'FSMOKES_TX', 'FHBA1C_TX_FIRST_YEAR', 'FBPS_TX_FIRST_YEAR',
                 'FHDL_TX_FIRST_YEAR', 'FLDL_TX_FIRST_YEAR', 'FTRG_TX_FIRST_YEAR',
                 'FSCREAT_TX_FIRST_YEAR', 'MI_HIST', 'STROKE_HIST', 'CHF_HIST',
                 'ANGINA_HIST', 'DIALYSIS_HIST', 'EGFR_60_HIST', 'EGFR_30_HIST',
                 'REVASC_HIST', 'FOOT_ULCER_HIST', 'BLINDNESS_HIST', 'NEUROP_HIST',
                 'LASER_HIST', 'AMP_HIST', 'MICRO_HIST', 'MACRO_HIST', 'FHBA1C',
                 'FBMI', 'FBPS', 'FHDL', 'FLDL', 'LN_FTRG', 'FSCREAT', 'FSMOKES',
                 'FTRG', 'BASE_FTRG', 'FFPG', 'FEGFR', 'WTMEC', ' US_POP_PROB ',
                 'WTSAF', 'SDMVPSU', 'SDMVSTRA', 'BASE_FHBA1C', 'BASE_FBMI',
                 'BASE_FBPS', 'BASE_FHDL', 'BASE_FLDL', 'LN_BASE_FTRG',
                 'BASE_FSCREAT', 'BASE_FSMOKES', 'Extras:', 'FAMILY_HISTORY',
                 'WAVE', 'TYPE_1_DIABETES', 'TYPE_2_DIABETES_TOTAL', 'FCHL',
                 'TYPE_2_DIABETES_UNDIAGNOSED', 'TYPE_2_DIABETES_DIAGNOSED']

    converted_df.drop(DROP_COLS, axis=1, inplace=True)
    converted_df.drop(converted_df.columns[converted_df.columns.str.contains('unnamed',
                                                                             case=False)],
                      axis=1, inplace=True)

    converted_df['lifespan'] = 0
    converted_df['should_update'] = 1
    converted_df['deceased'] = 0
    converted_df["cvd"] = "[0]"
    converted_df["current_cvd_death"] = "[0]"
    converted_df["ever_cvd_death"] = "[0]"
    converted_df["non_cvd_death"] = "[0]"
    converted_df["death"] = "[0]"
    converted_df["qaly"] = "[1]"
    converted_df["health_cost"] = "[0]"

    converted_df['hypoglycemia_medical'] = "[0]"
    converted_df['hypoglycemia_any'] = "[0]"

    converted_df.to_csv(os.path.join(OUTPUT_DIR, 't2d_nhanes.csv'), index=False)


def process_jhs():
    column_rename = {
        'ID': 'seqn', 'AGE': 'age_entry', 'DUR_YR00': 'diabetes_duration_entry',
        'EDUCOLL': 'has_postsecondary_ed', 'OBSEXREC': 'female',
        'BLACK': 'black', 'HISPANIC': 'hispanic', 'OTHER_RACE': 'other_race'
    }

    raw_population_df = pd.read_csv(os.path.join(INPUT_DIR, 'JHS_baseline_input_diabetes.csv'))
    raw_population_df.rename(columns=column_rename, inplace=True)
    raw_population_df['diabetes_duration_entry'].fillna(0, inplace=True)

    def apply(row):
        new_row = copy.deepcopy(row)
        new_row['age'] = int(row['age_entry'])
        new_row['bmi'] = "[{}]".format(row['FBMI'])
        new_row['sbp'] = "[{}]".format(row['FBPS'])
        new_row['hba1c'] = "[{}]".format(row['FHBA1C'])
        new_row['hdl'] = "[{}]".format(row['FHDL'])
        new_row['ldl'] = "[{}]".format(row['FLDL'])
        new_row['smoker'] = "[{}]".format(int(row['FSMOKES']))
        new_row['serum_creatinine'] = "[{}]".format(row['FSCREAT'])
        new_row['trig'] = "[{}]".format(row['LN_FTRG'])

        new_row['la_trial_first_year'] = 0
        new_row['intensive_la_treatment'] = 0
        new_row['intensive_la_treatment_first_year'] = 0
        new_row['hba1c_treatment_first_year'] = 0
        new_row['hba1c_treatment'] = 0
        new_row['sbp_treatment_first_year'] = 0
        new_row['sbp_treatment'] = 0
        new_row['hdl_treatment_first_year'] = 0
        new_row['hdl_treatment'] = 0
        new_row['ldl_treatment_first_year'] = 0
        new_row['ldl_treatment'] = 0
        new_row['trig_treatment_first_year'] = 0
        new_row['trig_treatment'] = 0
        new_row['serum_creatinine_treatment_first_year'] = 0
        new_row['serum_creatinine_treatment'] = 0
        new_row['smoker_treatment'] = 0

        new_row['amputation'] = "[{}]".format(int(row['AMP_HIST']))
        new_row['macroalbuminuria'] = "[{}]".format(int(row['MACRO_HIST']))
        new_row['microalbuminuria'] = "[{}]".format(int(row['MICRO_HIST']))
        new_row['blindness'] = "[{}]".format(int(row['BLINDNESS_HIST']))
        new_row['ulcer'] = "[{}]".format(int(row['FTULCER_HIST']))
        new_row['mi'] = "[{}]".format(int(row['MI_HIST']))
        new_row['stroke'] = "[{}]".format(int(row['STROKE_HIST']))
        new_row['chf'] = "[{}]".format(int(row['CHF_HIST']))
        new_row['angina'] = "[{}]".format(int(row['ANGINA_HIST']))
        new_row['dialysis'] = "[{}]".format(int(row['DIALYSIS_HIST']))
        new_row['egfr_60'] = "[{}]".format(int(row['EGFR60_HIST']))
        new_row['egfr_30'] = "[{}]".format(int(row['EGFR30_HIST']))
        new_row['revasc'] = "[{}]".format(int(row['REVASC_HIST']))
        new_row['neurop'] = "[0]"
        new_row['laser_retina'] = "[{}]".format(int(row['LASER_HIST']))

        new_row['la_trial'] = 0

        new_row['dataset'] = 'lookahead'

        return new_row

    converted_df = raw_population_df.apply(apply, axis=1)

    drop_cols = ['MI_HIST', 'STROKE_HIST', 'CHF_HIST', 'ANGINA_HIST', 'DIALYSIS_HIST',
                 'EGFR60_HIST', 'EGFR30_HIST', 'REVASC_HIST',
                 'BLINDNESS_HIST', 'LASER_HIST', 'AMP_HIST',
                 'MICRO_HIST', 'MACRO_HIST', 'FHBA1C', 'FBMI', 'FBPS', 'FHDL',
                 'FLDL', 'LN_FTRG', 'FSCREAT', 'FSMOKES'
                 ]

    converted_df.drop(drop_cols, axis=1, inplace=True)

    converted_df['lifespan'] = 0
    converted_df['should_update'] = 1
    converted_df['deceased'] = 0
    converted_df["current_cvd_death"] = "[0]"
    converted_df["ever_cvd_death"] = "[0]"
    converted_df["non_cvd_death"] = "[0]"
    converted_df["death"] = "[0]"
    converted_df["qaly"] = "[1]"
    converted_df["health_cost"] = "[0]"
    converted_df['hypoglycemia_medical'] = "[0]"
    converted_df['hypoglycemia_any'] = "[0]"
    converted_df['dialysis'] = "[0]"

    converted_df['glycemic drug'] = "[0]"
    converted_df['bp drug'] = "[0]"
    converted_df['statin type'] = "[0]"
    converted_df['smoking intervention'] = "[0]"
    converted_df['quit_smoking'] = "[0]"
    converted_df['accord'] = 0

    def get_cvd(row):
        if (
                row['mi'] == '[1]' or
                row['chf'] == '[1]' or
                row['stroke'] == '[1]' or
                row['revasc'] == '[1]' or
                row['angina'] == '[1]'
        ):
            return "[1]"
        return "[0]"

    converted_df['cvd'] = converted_df.apply(lambda x: get_cvd(x), axis=1)

    converted_df.to_csv(os.path.join(OUTPUT_DIR, 't2d-jhs.csv'), index=False)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Type 2 Diabetes Population Preprocessing')
    arg_parser.add_argument('--input',
                            choices=['lookahead_accord', 'nhanes', 'jhs'],
                            default='lookahead_accord',
                            help='Input population to use (default: %(default)s')
    args = arg_parser.parse_args()

    fns = {
        'nhanes': process_nhanes,
        'lookahead_accord': process_lookahead_accord,
        'jhs': process_jhs
    }

    fns[args.input]()
