# Steelplant Twin

Astana IT University diploma practical project for the topic "Virtual plant
models for efficient energy consumption using Machine Learning".

This repository implements a simulation-based proof of concept for a virtual
steel plant compressed-air system. It demonstrates the practical pipeline:

```text
virtual sensors -> MQTT -> InfluxDB -> Grafana -> ML
```

The project purpose is to generate synthetic telemetry, stream it through an
IoT time-series pipeline, visualize operational indicators, and train ML models
to predict `SEC` as the energy-efficiency KPI.

## Scope and Limitations

This is not a real industrial deployment. The simulator does not connect to
plant equipment, PLC/SCADA systems, or real compressor sensors. SEC is a
simulation proxy for Specific Energy Consumption and is useful for demonstrating
data flow, visualization, and ML workflow only.

The dataset is synthetic: 30 days of telemetry at a 5-minute interval, giving
8640 rows. ML metrics are evidence for the synthetic proof of concept, not a
claim of real industrial accuracy.

## Fixed Project Constants

- MQTT topic: `steelplant/compressed_air/telemetry`
- InfluxDB URL: `http://localhost:8086`
- Grafana URL: `http://localhost:33000`
- InfluxDB organization: `steelplant`
- InfluxDB bucket: `telemetry`
- InfluxDB measurement: `compressed_air_telemetry`
- Dataset size: 30 days, 5-minute interval, 8640 rows
- KPI / ML target: `SEC`
- ML models: Linear Regression baseline and Random Forest main model
- Train/test split: chronological 80/20
- Metrics: MAE, RMSE, R2

## Repository Structure

- `simulator/` - virtual telemetry generation and MQTT publisher.
- `ingestion/` - MQTT subscriber that writes telemetry to InfluxDB.
- `ml/` - SEC regression training pipeline and artifact export.
- `grafana/` - Grafana datasource, dashboard provisioning, and dashboard JSON.
- `data/processed/` - generated ML dataset output.
- `docs/ml/` - generated ML metrics, predictions, and plots.
- `docs/screenshots/` - evidence screenshots for the practical defense.
- `docs/evidence/README.md` - screenshot checklist and evidence descriptions.
- `docs/demo_runbook.md` - terminal-by-terminal demo order.
- `tests/` - unit tests for simulator, ingestion, publisher, and ML pipeline.
- `docker-compose.yml` - MQTT, InfluxDB, and Grafana services.
- `requirements.txt` - Python dependencies.

The authoritative telemetry schema is defined in `docs/02_data_contract.md`.

## Environment Setup

Install Python dependencies from the repository root:

```cmd
python -m pip install -r requirements.txt
```

Create a local `.env` file from `.env.example` and set local credentials and
the InfluxDB token:

```text
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_TOPIC=steelplant/compressed_air/telemetry

INFLUXDB_URL=http://localhost:8086
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=replace_with_your_password
INFLUXDB_ORG=steelplant
INFLUXDB_BUCKET=telemetry
INFLUXDB_TOKEN=replace_with_your_token

GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=replace_with_your_password
GRAFANA_INFLUXDB_URL=http://influxdb:8086
```

Do not commit `.env`, tokens, passwords, or local virtual environments.

## Docker Compose Startup

Start the MQTT broker, InfluxDB, and Grafana:

```cmd
docker compose up -d
docker compose ps
```

Services:

- `mqtt` exposes MQTT on port `1883`.
- `influxdb` exposes InfluxDB at `http://localhost:8086`.
- `grafana` exposes Grafana at `http://localhost:33000`.

InfluxDB and Grafana use persistent Docker volumes defined in
`docker-compose.yml`.

For the exact defense demo order, use `docs/demo_runbook.md`.

## Telemetry Ingestion and Publisher

Start the MQTT-to-InfluxDB subscriber first and keep it running:

```cmd
python -m ingestion.mqtt_to_influx
```

The subscriber listens on `steelplant/compressed_air/telemetry` and writes
points to InfluxDB measurement `compressed_air_telemetry`.

In another terminal, start the virtual telemetry publisher:

```cmd
python -m simulator.publisher
```

The publisher sends JSON MQTT payloads generated from `simulator.generator` and
publishes the telemetry fields from `docs/02_data_contract.md`. The simulation
metadata field `inefficient_scenario` is used only inside generator/tests; it is
not published to MQTT and is not written to InfluxDB.

## InfluxDB Verification

Open the InfluxDB UI:

```text
http://localhost:8086
```

The generator uses timestamps from `2026-04-01T00:00:00Z` through
`2026-04-30T23:55:00Z`. Use this Flux query in Data Explorer:

```flux
from(bucket: "telemetry")
  |> range(start: 2026-04-01T00:00:00Z, stop: 2026-05-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "compressed_air_telemetry")
  |> limit(n: 20)
```

To verify SEC values:

```flux
from(bucket: "telemetry")
  |> range(start: 2026-04-01T00:00:00Z, stop: 2026-05-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "compressed_air_telemetry")
  |> filter(fn: (r) => r._field == "SEC")
  |> limit(n: 20)
```

Expected result: records are present with payload timestamps and fields such as
`ambient_temperature`, `compressed_air_demand`, `pressure_setpoint`,
compressor states, `total_airflow`, `pressure_deviation`, and `SEC`.

## Grafana Dashboard

Open Grafana:

```text
http://localhost:33000
```

Use the credentials from `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`.
Grafana provisioning is included in the repository:

- datasource provisioning: `grafana/provisioning/datasources/influxdb.yml`
- dashboard provisioning: `grafana/provisioning/dashboards/dashboards.yml`
- dashboard JSON files: `grafana/dashboards/`

After `docker compose up -d`, Grafana creates the `Steelplant InfluxDB`
datasource using `GRAFANA_INFLUXDB_URL`, `INFLUXDB_ORG`, `INFLUXDB_BUCKET`, and
`INFLUXDB_TOKEN`. The dashboard should appear in the `Steelplant` folder.

If the dashboard does not appear, import the JSON manually from:

```text
grafana/dashboards/steelplant_compressed_air_dashboard.json
```

Expected dashboard evidence includes SEC, compressed-air demand, total airflow,
pressure deviation, active compressor count, and compressor 2 load level.

## ML SEC Regression Pipeline

Run the ML pipeline:

```cmd
python -m ml.train_sec_regression
```

The pipeline builds the 8640-row synthetic dataset from the simulator, keeps
`timestamp` only as metadata, excludes leakage features such as `SEC`,
`total_power_consumption`, and `energy_consumption` from model inputs, then
trains:

- Linear Regression baseline
- Random Forest main model with `random_state=42`

Evaluation uses a chronological 80/20 train/test split and reports MAE, RMSE,
and R2.

Generated outputs:

- `data/processed/ml_dataset.csv`
- `docs/ml/metrics.csv`
- `docs/ml/predictions.csv`
- `docs/ml/actual_vs_predicted_sec.png`
- `docs/ml/feature_importance.png`

## Evidence Screenshots

Evidence screenshots are stored in:

```text
docs/screenshots/
```

The evidence checklist is in `docs/evidence/README.md`. Screenshots should show
the Docker services, MQTT ingestion, telemetry publishing, InfluxDB/Grafana
evidence, ML outputs, pytest result, and ruff result. Do not add screenshots or
results that were not produced by the project.

## Testing and Validation

Run these checks from the repository root:

```cmd
python -m pytest
python -m ruff check .
docker compose config --quiet
```

For a full demo sequence, run the commands in `docs/demo_runbook.md`.
