# Assignment 4 (Simulation-Based) — Evidence Pack: What to Screenshot

Your assignment requires (1) repo link and (2) screenshots proving implementation started.

## A1 — Repository link (required)
- Screenshot of your GitHub/GitLab repo home page (shows name + files)
- Copy the repo URL into the report (Section 4.1)

## A2 — Created project workspace (required)
Goal: show project created and structured.
**Screenshot:** VS Code / PyCharm file tree showing:
- `docker-compose.yml`
- `simulator/`, `ingestion/`, `analytics/`, `docs/`
Tip: collapse folders so the structure is visible.

Caption example:
> Figure 2. Created project workspace in VS Code showing repository structure.

## A3 — Initial system model (required)
Goal: show architecture exists (system model).
**Option 1 (recommended):** create diagram in draw.io:
- components: Simulator → MQTT (Mosquitto) → Ingestion → InfluxDB → KPI script → Dashboard (Grafana)
**Screenshot:** draw.io tab with the diagram open.

Caption example:
> Figure 1. System architecture (initial system model) showing telemetry data flow and trust boundaries.

## A4 — First simulated component OR data flow (required)
Goal: show at least one working path.

Minimum set of screenshots (pick any 1–2):
1) Terminal running simulator (`publisher.py`) showing publish logs  
2) Terminal running ingestion (`mqtt_to_influx.py`) showing messages written to InfluxDB  
3) InfluxDB UI (Data Explorer) showing telemetry points  
4) KPI script output + saved plot `docs/kpi_kwh_per_ton.png`

Caption example:
> Figure 3. First simulated data flow: simulator publishes telemetry to MQTT, ingestion writes to InfluxDB (console evidence).

## A5 (recommended) — KPI output
- Screenshot of the KPI console output OR the saved plot file opened.

Caption example:
> Figure 4. KPI computation output (kWh/ton) from simulated heats.

## Mapping to report placeholders
- Report Section 2: replace "Figure 1" placeholder with architecture screenshot.
- Report Section 4: replace "Figure 2/3" placeholders with workspace + data flow screenshots.
- Appendix A: list A1–A5 items with short captions.

