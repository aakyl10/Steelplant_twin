---
name: ml-sec-regression-skill
description: Use this skill when working on the ML part for SEC prediction, including dataset export, feature selection, model training, metrics, plots, or ML review.
---

Purpose:
Help Codex implement and review a proof-of-concept supervised regression pipeline for SEC prediction.

Task type:
supervised regression

Target:
SEC

Forbidden feature:
total_power_consumption

Reason:
total_power_consumption must not be used as a feature because SEC is derived from energy or power, which can create data leakage.

Required features:
- ambient_temperature
- compressed_air_demand
- pressure_setpoint
- compressor_1_state
- compressor_2_state
- compressor_2_load_level
- active_compressors_count
- total_airflow
- pressure_deviation

Required split:
- chronological split;
- first 80% train;
- last 20% test;
- no separate validation split.

Required models:
- Linear Regression as baseline;
- Random Forest Regressor as main model.

Required metrics:
- MAE
- RMSE
- R2

Required plots:
- Actual vs Predicted SEC
- Feature Importance

Quality checks:
- check for data leakage;
- check that target is SEC;
- check that total_power_consumption is not used;
- check for missing values;
- check for duplicate timestamps;
- check for contradictory compressor states;
- keep the implementation simple and reproducible.