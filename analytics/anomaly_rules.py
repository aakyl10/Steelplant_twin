"""Optional: simple rule-based anomaly flags (demo only).

If kWh/ton > threshold, write an 'alert' point to InfluxDB.
"""

from datetime import datetime, timezone
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from common import CONFIG

THRESHOLD_KWH_PER_TON = 55.0  # adjust based on your simulated output


def main():
    if not CONFIG.influx_token:
        raise SystemExit("INFLUX_TOKEN is empty. Create .env.example and set INFLUX_TOKEN.")

    client = InfluxDBClient(url=CONFIG.influx_url, token=CONFIG.influx_token, org=CONFIG.influx_org)
    query_api = client.query_api()

    flux = f'''
from(bucket: "{CONFIG.influx_bucket}")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "kpi_eaf")
  |> filter(fn: (r) => r._field == "kwh_per_ton")
  |> last()
'''
    df = query_api.query_data_frame(flux)
    if df is None or (hasattr(df, "empty") and df.empty):
        print("No KPI data yet.")
        return

    val = float(df["_value"].iloc[-1])
    heat_id = str(df["heat_id"].iloc[-1]) if "heat_id" in df.columns else "unknown"

    if val > THRESHOLD_KWH_PER_TON:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        record = {
            "measurement": "alerts",
            "tags": {"type": "kwh_per_ton_high", "heat_id": heat_id},
            "fields": {"value": val, "threshold": THRESHOLD_KWH_PER_TON},
            "time": datetime.now(timezone.utc),
        }
        write_api.write(bucket=CONFIG.influx_bucket, record=record)
        print(f"ALERT: heat={heat_id} kWh/ton={val} > {THRESHOLD_KWH_PER_TON}")
    else:
        print(f"OK: heat={heat_id} kWh/ton={val} <= {THRESHOLD_KWH_PER_TON}")


if __name__ == "__main__":
    main()
