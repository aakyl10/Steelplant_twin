# Data Contract

## Purpose

This document is the source of truth for telemetry identifiers, fields, data
types, and validation rules in the virtual compressed-air plant.

The same data contract must be used by:

- telemetry generator
- MQTT payload
- InfluxDB storage
- dataset export
- ML training pipeline

The goal is to keep the IoT and ML parts consistent.

---

## Transport and storage identifiers

| Item | Value |
|---|---|
| MQTT topic | `steelplant/compressed_air/telemetry` |
| InfluxDB organization | `steelplant` |
| InfluxDB bucket | `telemetry` |
| InfluxDB measurement | `compressed_air_telemetry` |
| Timestamp source | `timestamp` payload field |

The default environment variables are documented in `.env.example`.

---

## Expected dataset size

The simulation must generate exactly 8640 rows.

Formula:

30 days * 24 hours * 12 intervals per hour = 8640 rows

Reason:

- 1 hour has 12 five-minute intervals
- 1 day has 24 hours
- 30 days gives 30 * 24 * 12 = 8640 rows

---

## Required telemetry fields

| Field | JSON/Python type | InfluxDB storage | Unit | ML role | Description |
|---|---|---|---|---|---|
| timestamp | string | point timestamp | ISO 8601 UTC | index | Measurement time |
| ambient_temperature | float | field | C | feature | Simulated ambient temperature |
| compressed_air_demand | float | field | m3/min | feature | Demand for compressed air |
| pressure_setpoint | float | field | bar | feature | Required pressure level |
| compressor_1_state | int | field | 0/1 | feature | Base compressor state |
| compressor_2_state | int | field | 0/1 | feature | Secondary compressor state |
| compressor_2_load_level | float | field | percent | feature | Load level of compressor 2 |
| active_compressors_count | int | field | count | feature | Number of active compressors |
| total_airflow | float | field | m3/min | feature | Produced airflow |
| pressure_deviation | float | field | bar | feature | Difference between target and actual pressure |
| SEC | float | field | kWh/m3 proxy | target | Specific Energy Consumption |

Only these required telemetry fields are published to MQTT and written to
InfluxDB. Internal simulation metadata, for example `inefficient_scenario`, is
not part of the MQTT payload, InfluxDB point, or ML feature set.

SEC is calculated as a positive simulation proxy for energy efficiency analysis.
It is not a physically validated compressor energy model.

---

## Required ML features

The ML model must use these features:

- ambient_temperature
- compressed_air_demand
- pressure_setpoint
- compressor_1_state
- compressor_2_state
- compressor_2_load_level
- active_compressors_count
- total_airflow
- pressure_deviation

Target:

- SEC

Forbidden feature:

- total_power_consumption

Reason:

total_power_consumption must not be used as a feature because SEC is derived from energy or power. Using it can create data leakage.

---

## Validation rules

### General rules

- All required fields must be present.
- Final ML dataset must not contain missing values.
- Timestamps must not be duplicated.
- SEC must be positive.
- The final dataset must contain exactly 8640 rows.

### Compressor rules

- compressor_1_state must be 0 or 1.
- compressor_2_state must be 0 or 1.
- active_compressors_count must match compressor states.
- If compressor_2_state = 0, compressor_2_load_level must be 0.
- If compressor_2_state = 1, compressor_2_load_level must be between 40 and 100.
- Compressor 1 normally works as the base compressor.
- Compressor 2 turns on when demand increases beyond base capacity.

### Pressure and airflow rules

- pressure_setpoint must be positive.
- total_airflow must be positive.
- pressure_deviation may be positive or negative.
- compressed_air_demand must be positive.

---

## Example valid telemetry row

| Field | Example value |
|---|---|
| timestamp | 2026-04-24T10:00:00Z |
| ambient_temperature | 24.5 |
| compressed_air_demand | 72.3 |
| pressure_setpoint | 7.0 |
| compressor_1_state | 1 |
| compressor_2_state | 1 |
| compressor_2_load_level | 55.0 |
| active_compressors_count | 2 |
| total_airflow | 75.0 |
| pressure_deviation | 0.12 |
| SEC | 0.118 |

---

## Schema maintenance

Use this document as the source of truth for telemetry fields and validation rules.

Do not rename fields without updating:

- docs/01_iot_plan.md
- docs/03_ml_plan.md
- code
- tests

Any generated dataset, MQTT payload, InfluxDB record, and ML DataFrame must follow this contract.
