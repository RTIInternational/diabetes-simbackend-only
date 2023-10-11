# Mapping of economist variables to platform variable:

| Econ Variable | Platform Variable | Notes |
|---|---|---|
| AGE | age_entry | |
| DUR_YR00 | diabetes_duration_entry | |
| EDUCOLL | has_postsecondary_ed | |
| OBSEXREC | female | |
| BLACK | black | |
| HISPANIC | hispanic | |
| OTHER_RACE | other_race | |
| CURSMOKE | curr_smoker | get_event_in_step(individual, 'smoker', step) |
| TWD_BMI | twd_bmi | time_weighted_risk_factor(individual, 'bmi') |
| TWD_BPS | twd_sbp | time_weighted_risk_factor(individual, 'sbp') |
| TWD_LDL | twd_ldl | time_weighted_risk_factor(individual, 'ldl') |
| TWD_HDL | twd_hdl | time_weighted_risk_factor(individual, 'hdl') |
| TWD_HBA1C | twd_hba1c | time_weighted_risk_factor(individual, 'hba1c') |
| TWD_TRG | twd_trig | time_weighted_risk_factor(individual, 'trig') |
| TWD_SCREAT | twd_serum_creatinine | time_weighted_risk_factor(individual, 'serum_creatinine') |
| LAG_ANGINA | lagged_angina | has_event_in_simulation(individual, 'angina') |
| LAG_MICRO | lagged_micro | has_event_in_simulation(individual, 'microalbuminuria') |
| LAG_MACRO | lagged_macro | has_event_in_simulation(individual, 'macroalbuminuria') |
| LAG_EGFR_60 | lagged_egfr_60 | has_event_in_simulation(individual, 'egfr_60') |
| LAG_EGFR_30 | lagged_egfr_30 | has_event_in_simulation(individual, 'egfr_30') |
| LAG_DIALYSIS | lagged_dialysis | has_event_in_simulation(individual, 'dialysis') |
| REVASC_HIST | ever_revasc | has_history(individual, 'revasc', step) |
| STROKE_HIST | ever_stroke | has_history(individual, 'stroke', step) |
| MI_HIST | ever_mi | has_history(individual, 'mi', step) |
| CHF_HIST | ever_chf  has_history(individual, 'chf', step) |
| YR1_MI | lag_tv_mi | has_acute_event(individual, 'mi', step) |
| YR1_ANGINA | lag_tv_angina | has_acute_event(individual, 'angina', step) |