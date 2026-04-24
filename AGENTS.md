# Project Guidance for Codex

## Project goal

This project implements a simulation-based IoT/IIoT virtual compressed-air plant for energy efficiency analysis using machine learning.

## Core architecture

virtual sensors -> MQTT -> InfluxDB -> Grafana -> export to ML

## Main KPI

SEC is the main KPI and the ML target.

SEC means Specific Energy Consumption.

## Important ML constraint

Do not use total_power_consumption as an ML feature when predicting SEC.

Reason:
SEC is derived from energy/power, so using total power consumption as a feature can create data leakage.

## IoT telemetry variables

Required fields:
- timestamp
- ambient_temperature
- compressed_air_demand
- pressure_setpoint
- compressor_1_state
- compressor_2_state
- compressor_2_load_level
- active_compressors_count
- total_airflow
- pressure_deviation
- SEC

## IoT simulation rules

- Generate 30 days of data.
- Use 5-minute interval.
- Expected dataset size: 8640 rows.
- Demand should follow a smooth daily pattern.
- Include one inefficient scenario.
- Compressor 1 works as the base compressor.
- Compressor 2 turns on when demand increases beyond base capacity.
- Compressor 2 load must be between 40% and 100% when active.
- Compressor 2 load must be 0 when inactive.
- SEC must be calculated at every step.

## ML requirements

Task type:
supervised regression

Target:
SEC

Features:
- ambient_temperature
- compressed_air_demand
- pressure_setpoint
- compressor_1_state
- compressor_2_state
- compressor_2_load_level
- active_compressors_count
- total_airflow
- pressure_deviation

Models:
- Linear Regression as baseline
- Random Forest Regressor as main model

Split:
- chronological split
- first 80% train
- last 20% test
- no separate validation split

Metrics:
- MAE
- RMSE
- R2

Plots:
- Actual vs Predicted SEC
- Feature Importance

## Commands

Install dependencies:
pip install -r requirements.txt

Run tests:
python -m pytest

Run linter:
python -m ruff check .

Run simulator:
python -m simulator.generator

Export dataset:
python -m analytics.export_dataset

Train baseline:
python -m ml.train_baseline

Train main model:
python -m ml.train_model

## Coding rules

- Keep Python simple and readable.
- Avoid over-engineering.
- Keep functions small and testable.
- Do not hardcode secrets.
- Do not commit .env.
- Do not rewrite unrelated files.
- Update tests when logic changes.
- Update docs when project behavior changes.

## Done means

Before finishing a task, Codex should return:
- changed files;
- what was implemented;
- how to run/check the result;
- assumptions or limitations.