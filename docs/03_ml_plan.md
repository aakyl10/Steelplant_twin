# ML Plan

## Goal

Build a proof-of-concept supervised regression model to predict SEC.

## Task type

Supervised regression.

## Target

SEC

## Forbidden feature

Do not use total_power_consumption as a feature.

## Features

- ambient_temperature
- compressed_air_demand
- pressure_setpoint
- compressor_1_state
- compressor_2_state
- compressor_2_load_level
- active_compressors_count
- total_airflow
- pressure_deviation

## Dataset

- 8640 rows
- no missing values
- no contradictory compressor values
- final CSV/DataFrame

## Split

- chronological split
- 80% train
- 20% test
- no separate validation split

## Baseline model

Linear Regression

## Main model

Random Forest Regressor

## Metrics

- MAE
- RMSE
- R2

## Plots

- Actual vs Predicted SEC
- Feature Importance

## Interpretation questions

- Does higher pressure setpoint increase SEC?
- Does the model reflect the inefficient scenario?
- Is Random Forest better than Linear Regression?