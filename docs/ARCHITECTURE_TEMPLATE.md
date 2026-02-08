# Architecture diagram template (for draw.io)

Create a diagram with these blocks (left → right):

1) **Simulator (publisher.py)**  
   - generates JSON telemetry: power_kw, energy_kwh_total, mode, heat_id, tons

2) **MQTT Broker (Mosquitto)**  
   - topic: `steelplant/eaf01/telemetry`
   - trust boundary: OT/Edge → OT-DMZ

3) **Ingestion Service (mqtt_to_influx.py)**  
   - validates schema + ranges
   - writes telemetry points to TSDB

4) **Time-series DB (InfluxDB)**  
   - measurement `telemetry_eaf`
   - measurement `kpi_eaf`

5) **Analytics (kpi_kwh_per_ton.py)**  
   - computes KPI per heat: kWh/ton
   - optional alerting / anomaly rules later

6) **Dashboard (Grafana)** (optional in Assignment 4)  
   - show KPI trend + basic alerts

Add dashed lines for trust boundaries and label them (OT, OT-DMZ, IT).

