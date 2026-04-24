# ML Plan

## Goal

Build a conservative proof-of-concept supervised regression pipeline to predict
SEC from simulated compressed-air telemetry.

## Task type

Supervised regression.

## Target

- `SEC`

SEC is a simulation proxy for Specific Energy Consumption. It is useful for
comparing operating conditions in this virtual plant, but it is not a physically
validated compressor energy model.

## Features

The model uses the exact project telemetry column names:

- `ambient_temperature`
- `compressed_air_demand`
- `pressure_setpoint`
- `compressor_1_state`
- `compressor_2_state`
- `compressor_2_load_level`
- `active_compressors_count`
- `total_airflow`
- `pressure_deviation`

`timestamp` is kept only as metadata in the output dataset and predictions.

## Excluded leakage features

The model must not use:

- `SEC` as an input feature
- `timestamp` as a numeric feature
- `total_power_consumption`
- `energy_consumption`
- any other direct power or energy total that could reconstruct SEC

## Dataset

The ML dataset is generated from the existing 30-day simulator output:

- 8640 rows
- 5-minute interval
- no missing values in selected features or target
- no contradictory compressor states
- saved to `data/processed/ml_dataset.csv`

## Split method

Chronological split:

- first 80% rows for training
- last 20% rows for testing
- no separate validation split

## Models

- Linear Regression as the baseline model
- RandomForestRegressor as the main model
- `random_state=42` for Random Forest

## Metrics

- MAE
- RMSE
- R2

Metrics are saved to `docs/ml/metrics.csv`.

## Outputs

- `data/processed/ml_dataset.csv`
- `docs/ml/metrics.csv`
- `docs/ml/predictions.csv`
- `docs/ml/actual_vs_predicted_sec.png`
- `docs/ml/feature_importance.png`

## Short interpretation

Linear Regression is used as a simple baseline. Random Forest is expected to
fit the non-linear rule-based SEC pattern better because the simulator contains
threshold behavior from compressor 2 activation and an inefficient operating
period. The near-perfect Random Forest score is caused by deterministic
synthetic data and should not be overclaimed as real industrial validation.
High model performance should be interpreted carefully because both the features
and target come from a deterministic simulation rather than measured industrial
data.
