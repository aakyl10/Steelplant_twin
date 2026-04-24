# Steelplant Twin

Simulation-based IoT/IIoT virtual compressed-air plant for energy efficiency
analysis. The IoT pipeline is:

```text
virtual sensors -> MQTT -> InfluxDB -> Grafana/export to ML
```

The authoritative telemetry schema is defined in `docs/02_data_contract.md`.

Academic note: SEC in this project is a simulation proxy for Specific Energy
Consumption. It is useful for demonstrating IoT data flow, visualization, and
ML workflow, but it is not a physically validated compressor energy model.

## IoT Pipeline Run Guide

### 1. Install Python dependencies

```cmd
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a local `.env` file from `.env.example` and set real local passwords and
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
```

Do not commit `.env`.

### 3. Start MQTT broker, InfluxDB, and Grafana

Start the Docker services:

```cmd
docker compose up -d
```

Services:

- `mqtt` exposes MQTT on port `1883`.
- `influxdb` exposes InfluxDB on port `8086`.
- `grafana` exposes Grafana at `http://localhost:33000`.

InfluxDB and Grafana use persistent Docker volumes defined in
`docker-compose.yml`.

### 4. Run MQTT-to-Influx subscriber

Start the subscriber first and keep it running:

```cmd
python -m ingestion.mqtt_to_influx
```

It subscribes to:

```text
steelplant/compressed_air/telemetry
```

It writes points to InfluxDB measurement:

```text
compressed_air_telemetry
```

### 5. Run telemetry publisher

In another terminal, publish generated telemetry:

```cmd
python -m simulator.publisher
```

The publisher uses rows from `simulator.generator`, sends JSON MQTT payloads,
and publishes only the required telemetry fields from `docs/02_data_contract.md`.
The simulation metadata field `inefficient_scenario` is used only inside the
generator/tests. It is not published to MQTT and is not written to InfluxDB.

### 6. Verify data in InfluxDB

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

Expected result: records are present with timestamps from the payload and fields
such as `ambient_temperature`, `compressed_air_demand`, `pressure_setpoint`,
compressor states, `total_airflow`, `pressure_deviation`, and `SEC`.

### 7. Open Grafana and review dashboard evidence

Open Grafana:

```text
http://localhost:33000
```

Use the credentials from `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`.
Grafana datasource and dashboard setup is manual in this proof of concept:
connect Grafana to InfluxDB, then create panels for the fields below.
The expected dashboard panels are:

- `SEC`
- `compressed_air_demand`
- `total_airflow`
- `pressure_deviation`
- `active_compressors_count`
- `compressor_2_load_level`

Evidence screenshots are stored in `docs/screenshots/`:

- `01_docker_compose_ps.png`
- `02_ingestion_subscribed.png`
- `03_publisher_8640_messages.png`
- `04_grafana_dashboard.png`
- `05_sec_panel_query.png`

## ML SEC Regression Pipeline

The ML pipeline is a conservative supervised regression proof of concept for
predicting `SEC` from the telemetry fields defined in `docs/02_data_contract.md`.
It generates the standard 8640-row dataset from the existing simulator, keeps
`timestamp` only as metadata, and excludes leakage features such as `SEC`,
`total_power_consumption`, and `energy_consumption` from the model inputs.

Run the pipeline from Windows CMD:

```cmd
python -m ml.train_sec_regression
```

Generated outputs:

- `data/processed/ml_dataset.csv`
- `docs/ml/metrics.csv`
- `docs/ml/predictions.csv`
- `docs/ml/actual_vs_predicted_sec.png`
- `docs/ml/feature_importance.png`

Verification commands:

```cmd
python -m pytest
python -m simulator.generator
python -m ml.train_sec_regression
python -m ruff check .
```

The baseline model is Linear Regression. The main model is
RandomForestRegressor with `random_state=42`. Metrics are MAE, RMSE, and R2
using a chronological 80/20 train/test split.
