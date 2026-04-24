# IoT Plan

## Goal

Build the architecture and data logic for a virtual compressed-air plant.

## Architecture

virtual sensors -> MQTT -> InfluxDB -> Grafana -> export to ML

## Telemetry variables

The authoritative telemetry schema is defined in `docs/02_data_contract.md`.

## Rule-based logic

- Compressor 1 works as the base compressor.
- Compressor 2 turns on when demand increases.
- Compressor 2 works in the 40-100% load range.
- SEC is calculated at every simulation step.

## Data generation

- 30 days
- 5-minute interval
- 8640 rows
- smooth daily demand
- one inefficient scenario

## MQTT

Topic:

```text
steelplant/compressed_air/telemetry
```

Example JSON payload:

```json
{
  "timestamp": "2026-04-24T10:00:00Z",
  "ambient_temperature": 24.5,
  "compressed_air_demand": 72.3,
  "pressure_setpoint": 7.0,
  "compressor_1_state": 1,
  "compressor_2_state": 1,
  "compressor_2_load_level": 55.0,
  "active_compressors_count": 2,
  "total_airflow": 75.0,
  "pressure_deviation": 0.12,
  "SEC": 0.118
}
```

## InfluxDB storage

Bucket:

```text
telemetry
```

Measurement:

```text
compressed_air_telemetry
```

Timestamp field:

```text
timestamp
```

Stored fields must follow `docs/02_data_contract.md`.

## Grafana dashboard panels

1. Demand and total airflow
2. Pressure setpoint and pressure deviation
3. Compressor states and compressor 2 load
4. SEC and inefficient scenario

## IoT part output

The IoT part should produce:

- architecture diagram
- variable table
- workflow of virtual plant
- data schema / payload example
- dashboard plan
