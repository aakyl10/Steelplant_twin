\# AGENTS.md



\## Project context



This repository is a diploma practical project for a simulation-based proof-of-concept virtual compressed-air plant.



Project topic:

Virtual plant models for efficient energy consumption using Machine Learning.



The project demonstrates:

\- virtual telemetry generation;

\- MQTT publishing;

\- MQTT-to-InfluxDB ingestion;

\- InfluxDB time-series storage;

\- Grafana visualization;

\- ML-based SEC regression;

\- tests and reproducible evidence.



\## Critical constraints



Do not change these unless explicitly requested:



\- MQTT topic: `steelplant/compressed\_air/telemetry`

\- InfluxDB organization: `steelplant`

\- InfluxDB bucket: `telemetry`

\- InfluxDB measurement: `compressed\_air\_telemetry`

\- Grafana external port: `33000`

\- Dataset size: `8640` rows

\- Main KPI / target: `SEC`

\- Main simulation scope: synthetic 30-day telemetry

\- Project character: simulation-based proof-of-concept, not real industrial deployment



\## Required validation commands



After code changes, run:



```powershell

python -m pytest

python -m ruff check 
After ML changes, also run:

python -m ml.train_sec_regression

After Docker/Grafana changes, also run:

docker compose down
docker compose up -d
docker compose ps
Style requirements
Keep the project Windows/PyCharm friendly.
Do not introduce Poetry, Conda, Kubernetes, Make-only workflows, or complex infrastructure.
Keep dependencies simple.
Do not commit real secrets, .env, tokens, passwords, or local virtual environments.
Prefer small, safe changes.
Do not overclaim real industrial accuracy.
Keep README commands consistent with actual project commands.
Diploma practical priorities

Highest priority:

Reproducibility
Working demo
Evidence screenshots
Clean repository
Passing tests
Clear ML outputs
Simple Docker/Grafana setup

Avoid unnecessary scope expansion.

