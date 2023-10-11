import os
import random
import ast

import pandas as pd
import numpy as np

from src.simulation.equations.models import *

BASE_DIR = os.path.join(os.path.join('scenarios'))

def parse_json(scenario, diabetes_type):
    risk_factors = scenario['risk_factors'][0]
    clinical_history = scenario['clinical_history'][0]

    mean_sd_demographics = scenario['demographics'][0]['mean_sd_demographics']
    other_proportions = scenario['demographics'][0]['other_proportions']
    race_proportions = scenario['demographics'][0]['race_proportions']

    value_dict = {}
    value_dict['pop size'] = int(scenario['size'])
    value_dict['age at entry mean'] = mean_sd_demographics['Age at entry mean']
    value_dict['age at entry sd'] = mean_sd_demographics['Age at entry sd']
    value_dict['proportion white'] = race_proportions['proportion_white']
    value_dict['proportion black'] = race_proportions['proportion_black']
    value_dict['proportion hispanic'] = race_proportions['proportion_hispanic']
    value_dict['proportion others'] = race_proportions['proportion_other']
    value_dict['proportion female'] = other_proportions['proportion_female']
    value_dict['proportion with postsecondary education'] = other_proportions['proportion_postsecondary_education']
    value_dict['proportion smokers'] = other_proportions['proportion_smoker']

    value_dict['bmi mean'] = risk_factors['BMI mean']
    value_dict['bmi sd'] = risk_factors['BMI sd']
    value_dict['sbp mean'] = risk_factors['SBP mean']
    value_dict['sbp sd'] = risk_factors['SBP sd']
    value_dict['hba1c mean'] = risk_factors['HBA1C mean']
    value_dict['hba1c sd'] = risk_factors['HBA1C sd']
    value_dict['hdl mean'] = risk_factors['HDL mean']
    value_dict['hdl sd'] = risk_factors['HDL sd']
    value_dict['ldl mean'] = risk_factors['LDL mean']
    value_dict['ldl sd'] = risk_factors['LDL sd']
    value_dict['serum_creatinine mean'] = risk_factors['Serum creatinine mean']
    value_dict['serum_creatinine sd'] = risk_factors['Serum creatinine sd']
    value_dict['trig mean'] = risk_factors['Triglycerides mean']
    value_dict['trig sd'] = risk_factors['Triglycerides sd']
    value_dict['diabetes_duration_entry mean'] = mean_sd_demographics['Diabetes duration entry mean']
    value_dict['diabetes_duration_entry sd'] = mean_sd_demographics['Diabetes duration entry sd']

    value_dict['proportion amputation'] = clinical_history['proportion_amputation']
    value_dict['proportion microalbuminuria'] = clinical_history['proportion_microalbuminuria']
    value_dict['proportion macroalbuminuria'] = clinical_history['proportion_macroalbuminuria']
    value_dict['proportion blindness'] = clinical_history['proportion_blindness']
    value_dict['proportion ulcer'] = clinical_history['proportion_foot_ulcer']
    value_dict['proportion mi'] = clinical_history['proportion_mi']
    value_dict['proportion stroke'] = clinical_history['proportion_stroke']
    value_dict['proportion chf'] = clinical_history['proportion_chf']
    value_dict['proportion angina'] = clinical_history['proportion_angina']
    value_dict['proportion dialysis'] = clinical_history['proportion_dialysis']
    value_dict['proportion egfr_60'] = clinical_history['proportion_egfr_60']
    value_dict['proportion egfr_30'] = clinical_history['proportion_egfr_30']
    value_dict['proportion revasc'] = clinical_history['proportion_revascularization']
    value_dict['proportion neurop'] = clinical_history['proportion_neuropathy']
    value_dict['proportion laser_retina'] = clinical_history['proportion_laser_retina']
    value_dict['proportion accord'] = clinical_history['proportion_from_accord_dataset']

    if diabetes_type == 'pre':
        value_dict['proportion family history'] = clinical_history['proportion_family_history']
        value_dict['fpg mean'] = risk_factors['FPG mean']
        value_dict['fpg sd'] = risk_factors['FPG sd']

    return value_dict


def do_roulette_wheel(rng, choices):
    max_value = sum(choices.values())
    pick = rng.uniform(0, max_value)
    current = 0
    for key, value in choices.items():
        current += value
        if current > pick:
            return key


def get_intervention_dict(type):
    t2d_factors = ["hba1c", "bmi", "sbp", "hdl", "ldl", "trig", "smoker", "serum_creatinine"]
    t2d_risks = ["microalbuminuria", "macroalbuminuria", "egfr_60", "egfr_30", "dialysis", "neuropathy", "ulcer",
                 "amputation", "laser_retin", "blindness", "mi", "stroke", "chf", "angina", "revasc",
                 "hypo_med", "hypo_any"]
    t2d_factor_dict = {key: 0 for key in t2d_factors}
    t2d_risk_dict = {key: 0 for key in t2d_risks}

    return {"factor_changes": t2d_factor_dict, "risk_reductions": t2d_risk_dict}


z_dict = {1: 2.57, 5: 1.960, 10: 1.645}


def get_risk_factor_changes(psa_rng, scenario, type):
    intervention_dict = get_intervention_dict(type)
    factor_contribution = {}
    basic_intervention_cost = {}
    if scenario['is_intervention']:
        interventions = scenario['intervention_set']['interventions'][0]
        intervention_types = ['generic_control', 'glycemic_control', 'cholesterol_control', 'bp_control']
        for intervention_short_name in intervention_types:
            intervention_name = intervention_short_name + '_intervention'
            intervention_type = intervention_short_name + '_setup_type'
            if intervention_name in interventions.keys():
                if intervention_name == 'generic_control_intervention':
                    setup_type = 'basic'
                else:
                    setup_type = interventions[intervention_name][intervention_type]
                if setup_type == 'basic':
                    # only pulls in factor changes and risk reductions
                    intervention = interventions[intervention_name][intervention_name][0]
                    basic_intervention_cost[intervention_name] = intervention['annual_cost']
                    factor_changes = intervention['factor_changes']
                    contrib_factor_dict = {}
                    for factor, change in factor_changes.items():
                        factor_change = intervention_dict['factor_changes'][factor]
                        # Looks like a hack but is the cleanest way to not vary anything given the factor calculation
                        # below when the population is generated
                        if change != 0 and scenario['psa_factor_change'] != 'Do not vary':
                            # print('before', change)
                            psa_factor_change = int(scenario['psa_factor_change'])
                            # psa_factor_change = int(''.join(filter(str.isdigit, scenario['psa_factor_change'])))
                            # We have input value (=mean) and selected significance level.
                            # Distribution is normal. Each significance level is associated
                            # with a corresponding Z value: 10%--1.645, 5%--1.960, 1%--2.576.
                            # Apply normal(mean, SE) = normal(mean, [abs(mean)]/[Z])
                            psa_change = normal.model(psa_rng, change, abs(change) / z_dict[psa_factor_change], 2)
                            # print('after', psa_change)
                            # several interventions may change the same factor so we add them up
                            intervention_dict['factor_changes'][factor] = factor_change + psa_change
                        else:
                            intervention_dict['factor_changes'][factor] = factor_change + change
                        # blood pressure intervention only applies to certain individuals so we need to record its
                        # contributions so we can subtract from the sum where applicable later
                        if intervention_name == 'bp_control_intervention':
                            contrib_factor_dict[factor] = change
                            factor_contribution['bp'] = contrib_factor_dict
                        # same as for the blood pressure intervention applies to the cholesterol intervention
                        if intervention_name == 'cholesterol_control_intervention':
                            contrib_factor_dict[factor] = change
                            factor_contribution['chol'] = contrib_factor_dict

    factor_changes = intervention_dict['factor_changes']

    return factor_changes, factor_contribution, basic_intervention_cost


def generate_t2d_population(rng_list, scenario):
    rng = rng_list[0]
    psa_rng = rng_list[1]
    value_dict = parse_json(scenario, 't2d')
    factor_changes, factor_contribution, basic_intervention_cost = get_risk_factor_changes(psa_rng, scenario, 't2d')
    if scenario['is_intervention']:
        applicable_interventions_list = scenario['intervention_set']['interventions'][0]['interventions_basic'][0]
    else:
        applicable_interventions_list = []

    scenario_interventions = scenario['intervention_set']['interventions'][0]

    people_list = []
    risk_factors = ''
    for _ in range(value_dict['pop size']):
        person_dict = {}

        age_entry = gamma.model(rng, value_dict['age at entry mean'], value_dict['age at entry sd'], 1)
        diabetes_duration = gamma.model(rng, value_dict['diabetes_duration_entry mean'],
                                        value_dict['diabetes_duration_entry sd'], 1)
        person_dict['diabetes_duration_entry'] = round(diabetes_duration)

        # to make sure individuals are not older > 95 and the difference diabetes duration and age is > 10
        while (age_entry - diabetes_duration < 10) and age_entry < 95:
            age_entry = gamma.model(rng, value_dict['age at entry mean'], value_dict['age at entry sd'], 1)
        person_dict['age_entry'] = round(age_entry)
        if age_entry > 95:
            person_dict['age_entry'] = 95
            dif = age_entry - 95
            person_dict['diabetes_duration_entry'] = round(person_dict['diabetes_duration_entry'] - dif)

        person_dict['female'] = dice.model(rng, value_dict['proportion female'])

        person_dict['white'] = 0
        person_dict['black'] = 0
        person_dict['hispanic'] = 0
        person_dict['other_race'] = 0
        choices = {'other_race': value_dict['proportion others'],
                   'black': value_dict['proportion black'],
                   'hispanic': value_dict['proportion hispanic'],
                   'white': value_dict['proportion white']}
        race = do_roulette_wheel(rng, choices)
        person_dict[race] = 1

        person_dict['has_postsecondary_ed'] = dice.model(rng, value_dict['proportion with postsecondary education'])

        risk_factor_dict = {}

        bmi = gamma.model(rng, value_dict['bmi mean'], value_dict['bmi sd'], 1)
        while bmi < 16:
            bmi = gamma.model(rng, value_dict['bmi mean'], value_dict['bmi sd'], 1)
        risk_factor_dict['bmi'] = bmi

        risk_factor_dict['sbp'] = gamma.model(rng, value_dict['sbp mean'], value_dict['sbp sd'], 1)

        hba1c = gamma.model(rng, value_dict['hba1c mean'], value_dict['hba1c sd'], 2)
        while hba1c < 4.8:
            hba1c = gamma.model(rng, value_dict['hba1c mean'], value_dict['hba1c sd'], 2)
        risk_factor_dict['hba1c'] = hba1c

        risk_factor_dict['hdl'] = gamma.model(rng, value_dict['hdl mean'], value_dict['hdl sd'], 1)

        ldl = gamma.model(rng, value_dict['ldl mean'], value_dict['ldl sd'], 2)
        while ldl < 24:
            ldl = gamma.model(rng, value_dict['ldl mean'], value_dict['ldl sd'], 2)
        risk_factor_dict['ldl'] = ldl

        risk_factor_dict['smoker'] = dice.model(rng, value_dict['proportion smokers'])

        serum_creatinine = gamma.model(rng, 
            value_dict['serum_creatinine mean'], value_dict['serum_creatinine sd'], 2)
        while serum_creatinine < 0.3:
            serum_creatinine = gamma.model(rng, 
                value_dict['serum_creatinine mean'], value_dict['serum_creatinine sd'], 2)
        risk_factor_dict['serum_creatinine'] = serum_creatinine

        risk_factor_dict['trig'] = gamma.model(rng, 
            value_dict['trig mean'], value_dict['trig sd'], 1)

        for intervention in ['generic', 'glycemic', 'cholesterol', 'bp']:
            person_dict[f'baseline {intervention} intervention'] = 0

        # record baseline intervention so cost can be calculated
        intervention_columns = []
        if scenario['is_intervention']:
            for intervention in ['generic', 'glycemic', 'cholesterol', 'bp']:
                if f'{intervention}_control_intervention' in basic_intervention_cost.keys():
                    basic_cost = basic_intervention_cost[f'{intervention}_control_intervention']
                    if applicable_interventions_list[f'type_{intervention}_t2d'] and basic_cost > 0:
                        person_dict[f'baseline {intervention} intervention'] = 1
                    else:
                        person_dict[f'baseline {intervention} intervention'] = 0
                intervention_columns.append(f'baseline {intervention} intervention')

        # apply factor change interventions where applicable
        if scenario['is_intervention']:
            basic_interventions = scenario['intervention_set']['interventions'][0]
            for factor, factor_change in factor_changes.items():
                if 'bp_control_intervention' in basic_interventions:
                    name = 'bp_control_intervention'
                    setup_type = basic_interventions[name]['bp_control_setup_type']
                    if setup_type == 'basic':
                        # for sbp apply risk factor changes and risk reductions only if sbp <
                        # than a user specified value
                        min_value = basic_interventions[name][name][0]['apply if greater than']
                        if factor == 'sbp' and risk_factor_dict['sbp'] < min_value:
                            factor_change = factor_change - factor_contribution['bp'][factor]
                            # individual did not receive this baseline intervention
                            person_dict['baseline bp intervention'] = 0
                if 'cholesterol_control_intervention' in basic_interventions:
                    name = 'cholesterol_control_intervention'
                    setup_type = basic_interventions[name]['cholesterol_control_setup_type']
                    if setup_type == 'basic':
                        # cholesterol changes are only applied if individual is older > user specified age
                        # for younger individuals we need to deduct changes because they were previously add together
                        max_age = basic_interventions[name][name][0]['age']
                        if person_dict['age_entry'] < max_age:
                            chol_contribution = factor_contribution['chol']
                            if factor == 'ldl':
                                factor_change = factor_change - chol_contribution['ldl']
                            if factor == 'hdl':
                                factor_change = factor_change - chol_contribution['hdl']
                            if factor == 'trig':
                                factor_change = factor_change - chol_contribution['trig']
                            # individual did not receive this baseline intervention
                            person_dict['baseline cholesterol intervention'] = 0
                risk_factor_dict[factor] = risk_factor_dict[factor] + factor_change

        person_dict['quit_smoking'] = "[0]"
        person_dict['smoker'] = f"[{risk_factor_dict['smoker']}]"
        person_dict['bmi'] = f"[{risk_factor_dict['bmi']}]"

        person_dict['hba1c'] = f"[{risk_factor_dict['hba1c']}]"
        person_dict['hdl'] = f"[{risk_factor_dict['hdl']}]"
        person_dict['ldl'] = f"[{risk_factor_dict['ldl']}]"
        person_dict['sbp'] = f"[{risk_factor_dict['sbp']}]"
        person_dict['serum_creatinine'] = f"[{risk_factor_dict['serum_creatinine']}]"
        person_dict['trig'] = f"[{risk_factor_dict['trig']}]"

        complication_dict = {'microalbuminuria': "microalbuminuria", 'macroalbuminuria': "macroalbuminuria",
                             'egfr_60': "egfr_60", 'egfr_30': "egfr_30", 'dialysis': "dialysis",
                             'neurop': "neuropathy", 'ulcer': "ulcer", 'amputation': "amputation",
                             'laser_retina': "laser_retin", 'blindness': "blindness", 'mi': "mi",
                             'stroke': "stroke", 'chf': "chf", 'angina': "angina", 'revasc': "revasc"}

        for complication in complication_dict.keys():
            person_dict[complication] = f"[{dice.model(rng, value_dict['proportion ' + complication])}]"

        person_dict['hypoglycemia_medical'] = "[0]"
        person_dict['hypoglycemia_any'] = "[0]"

        dialysis = dice.model(rng, value_dict['proportion dialysis'])
        person_dict['dialysis'] = f"[{dialysis}]"

        if dialysis:
            person_dict['egfr_60'] = f"[1]"
            person_dict['egfr_30'] = f"[1]"
        else:
            person_dict['egfr_60'] = f"[{dice.model(rng, value_dict['proportion egfr_60'])}]"
            egfr_30 = dice.model(rng, value_dict['proportion egfr_60'])
            person_dict['egfr_30'] = f"[{egfr_30}]"
            if egfr_30:
                person_dict['egfr_60'] = f"[1]"

        person_dict['neurop'] = f"[{dice.model(rng, value_dict['proportion neurop'])}]"
        person_dict['laser_retina'] = f"[{dice.model(rng, value_dict['proportion laser_retina'])}]"

        person_dict['age'] = person_dict['age_entry']
        person_dict['la_trial'] = 1
        person_dict['accord'] = dice.model(rng, value_dict['proportion accord'])
        person_dict['lifespan'] = 0
        person_dict['should_update'] = 1
        person_dict['deceased'] = 0

        person_dict['glycemic drug'] = "[0]"
        person_dict['bp drug'] = "[0]"
        person_dict['statin type'] = "[0]"
        person_dict[f'smoking intervention'] = "[0]"

        person_dict["cvd"] = "[0]"
        mi_int = ast.literal_eval(person_dict['mi'])[0]
        chf_int = ast.literal_eval(person_dict['chf'])[0]
        stroke_int = ast.literal_eval(person_dict['stroke'])[0]
        revasc_int = ast.literal_eval(person_dict['revasc'])[0]
        angina_int = ast.literal_eval(person_dict['angina'])[0]
        if sum([mi_int, chf_int, stroke_int, revasc_int, angina_int]) > 0:
            person_dict["cvd"] = "[1]"

        person_dict["current_cvd_death"] = "[0]"
        person_dict["ever_cvd_death"] = "[0]"
        person_dict["non_cvd_death"] = "[0]"
        person_dict["death"] = "[0]"
        person_dict["qaly"] = "[0]"
        person_dict["overall_cost"] = "[0]"
        person_dict["health_cost"] = "[0]"
        person_dict["event_cost"] = "[0]"
        person_dict["intervention_cost"] = "[0]"
        person_dict['hypoglycemia_medical'] = "[0]"
        person_dict['hypoglycemia_any'] = "[0]"

        person_dict['smoker_treatment'] = 0
        person_dict['la_trial_first_year'] = 0
        person_dict['intensive_la_treatment'] = 0
        person_dict['intensive_la_treatment_first_year'] = 0
        person_dict['hba1c_treatment_first_year'] = 0
        person_dict['hba1c_treatment'] = 0
        person_dict['sbp_treatment_first_year'] = 0
        person_dict['sbp_treatment'] = 0
        person_dict['hdl_treatment_first_year'] = 0
        person_dict['hdl_treatment'] = 0
        person_dict['ldl_treatment_first_year'] = 0
        person_dict['ldl_treatment'] = 0
        person_dict['trig_treatment_first_year'] = 0
        person_dict['trig_treatment'] = 0
        person_dict['serum_creatinine_treatment_first_year'] = 0
        person_dict['serum_creatinine_treatment'] = 0

        non_complier_columns = []
        interventions = ['glycemic', 'cholesterol', 'bp']
        for intervention in interventions:
            person_dict[f'{intervention}_non_compliant'] = 0
            non_complier_columns.append(f'{intervention}_non_compliant')
            if 'non-' in scenario['scenario_name']:
                continue
            else:
                control_key = f'{intervention}_control_intervention'
                if control_key in scenario_interventions:
                    if scenario_interventions[control_key][f'{intervention}_control_setup_type'] == 'advanced':
                        key = f'{intervention}_control_noncompliers'
                        non_com_data = scenario_interventions[f'{intervention}_control_intervention'][key]
                        proportion = non_com_data[0][f'{intervention}_non_compliant_t2d']
                        if random.random() <= proportion:
                            person_dict[f'{intervention}_non_compliant'] = 1

        people_list.append(person_dict)
        risk_factors = list(risk_factor_dict.keys())

    if sum(factor_changes.values()) == 0:
        return pd.DataFrame(people_list), non_complier_columns + intervention_columns
    return pd.DataFrame(people_list), risk_factors + non_complier_columns + intervention_columns


def generate_custom_population(seed, scenario_tuple, equation_set):
    population_df_dict = {}
    # first entry is the non-intervention one
    rng = np.random.default_rng(seed)
    psa_rng = np.random.default_rng(seed)
    population_df, _ = generate_t2d_population([rng, psa_rng], scenario_tuple[0])
    for scenario in scenario_tuple:
        rng = np.random.default_rng(seed)
        psa_rng = np.random.default_rng(seed)
        if 'non' in scenario['scenario_name']:
            population_df_dict[scenario['scenario_name']] = population_df
        else:
            intervention_df, intervention_columns = generate_t2d_population([rng, psa_rng], scenario)
            mod_population_df = population_df.drop(columns=intervention_columns)
            intervention_df = intervention_df[intervention_columns]
            mod_population_df = mod_population_df.join(intervention_df)
            mod_population_df = mod_population_df[population_df.columns]
            population_df_dict[scenario['scenario_name']] = mod_population_df

    return population_df_dict
