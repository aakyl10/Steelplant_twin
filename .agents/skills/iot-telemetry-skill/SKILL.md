---
name: iot-telemetry-skill
description: Use this skill when working on the virtual compressed-air plant IoT layer, telemetry generation, MQTT payloads, InfluxDB ingestion, or Grafana dashboard planning.
---

Purpose:
Help Codex implement and review the IoT part of the virtual compressed-air plant project.

Required architecture:
virtual sensors -> MQTT -> InfluxDB -> Grafana -> export to ML

Required telemetry fields:
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

Simulation requirements:
- generate 30 days of data;
- use a 5-minute interval;
- produce exactly 8640 rows;
- use smooth daily demand;
- include one inefficient scenario;
- calculate SEC at every step.

Compressor logic:
- compressor 1 is the base compressor;
- compressor 2 activates when demand increases beyond base capacity;
- compressor 2 load must be 0 when inactive;
- compressor 2 load must be between 40 and 100 when active;
- active_compressors_count must match compressor states.

Quality checks:
- no missing telemetry fields;
- no contradictory compressor values;
- JSON payload must match docs/02_data_contract.md;
- do not hardcode secrets;
- update tests when logic changes.