# Demo Runbook

This runbook gives the terminal order for the practical defense demo. Run all
commands from the repository root. The system is a simulation-based proof of
concept, not a real industrial deployment.

## Terminal 1

```cmd
docker compose down
docker compose up -d
docker compose ps
```

Expected result: MQTT, InfluxDB, and Grafana containers are created and shown by
`docker compose ps`. Grafana is available at `http://localhost:33000`;
InfluxDB is available at `http://localhost:8086`.

## Terminal 2

```cmd
python -m ingestion.mqtt_to_influx
```

Expected result: the subscriber connects to MQTT and listens on
`steelplant/compressed_air/telemetry`. Keep this terminal running while the
publisher sends telemetry.

## Terminal 3

```cmd
python -m simulator.publisher
```

Expected result: virtual compressed-air telemetry is published to MQTT and
ingested into InfluxDB measurement `compressed_air_telemetry` in bucket
`telemetry`.

## Terminal 4

```cmd
python -m ml.train_sec_regression
python -m pytest
python -m ruff check .
```

Expected result: the ML pipeline completes on the synthetic 8640-row dataset,
tests pass, and ruff reports no lint errors.

## Expected Output Files

- `data/processed/ml_dataset.csv`
- `docs/ml/metrics.csv`
- `docs/ml/predictions.csv`
- `docs/ml/actual_vs_predicted_sec.png`
- `docs/ml/feature_importance.png`
- `docs/screenshots/`

The ML metrics and plots are proof-of-concept evidence on generated telemetry.
They must not be presented as real industrial validation or real compressor
accuracy.
