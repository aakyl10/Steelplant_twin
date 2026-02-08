# Steel Plant Digital Twin (Simulation-Based IIoT) — Assignment 4 Evidence Starter

This repository provides a **minimal working implementation start** for a simulation-based IIoT digital twin:
**simulator → MQTT → ingestion → InfluxDB → KPI computation (kWh/ton)**.

It is intentionally small so you can run it on a laptop and quickly produce:
- a repository link,
- screenshots of workspace + system model + first data flow,
- a short simulation environment write-up.

## 1) Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Python 3.10+ (recommended 3.11)
- Git (optional but recommended)

## 2) Quick start (local run)

### Step A — configure environment
1. Copy `.env.example` to `.env`
2. Set `INFLUX_TOKEN` to a long random string (important)

### Step B — start services
```bash
docker compose up -d
```

Open InfluxDB UI:
- http://localhost:8086
Login using `INFLUX_USERNAME` / `INFLUX_PASSWORD` from `.env`

(Optional) Grafana:
- http://localhost:3000 (default admin/admin on first login)

### Step C — create Python virtual env and install deps
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### Step D — run the simulator (publisher)
```bash
python simulator/publisher.py
```

### Step E — run ingestion (subscriber + DB writer)
Open a **second terminal** (same venv):
```bash
python ingestion/mqtt_to_influx.py
```

### Step F — compute KPI (kWh/ton)
After 1–2 minutes of data:
```bash
python analytics/kpi_kwh_per_ton.py
```

The script prints KPI values and saves a plot:
- `docs/kpi_kwh_per_ton.png`

## 3) Evidence screenshots checklist (for Assignment 4)

See `docs/EVIDENCE.md` for **exact screenshot targets** and captions aligned with the report placeholders.

## 4) Security note
This repo includes an explicit **vulnerability / mitigation plan** (even for a simulation):
- `docs/SECURITY.md` (what is risky, why, and how to fix)
- `docs/VULNERABILITY_BACKLOG.md` (short backlog to show planning)

