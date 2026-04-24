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

Use the required ML feature list defined in `docs/02_data_contract.md`.

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
