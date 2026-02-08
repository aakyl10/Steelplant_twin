from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from common import CONFIG


def query_telemetry(client: InfluxDBClient, lookback_minutes: int = 120) -> pd.DataFrame:
    query_api = client.query_api()
    flux = f'''
from(bucket: "{CONFIG.influx_bucket}")
  |> range(start: -{lookback_minutes}m)
  |> filter(fn: (r) => r._measurement == "telemetry_eaf")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> keep(columns: ["_time","heat_id","mode","device_id","power_kw","energy_kwh_total","tons"])
'''
    tables = query_api.query_data_frame(flux)
    if isinstance(tables, list):
        df = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()
    else:
        df = tables
    if df.empty:
        return df

    # Influx pivot sometimes produces extra columns
    df = df.rename(columns={"_time": "time"})
    df["time"] = pd.to_datetime(df["time"], utc=True)
    # tags may appear as strings
    df["heat_id"] = df["heat_id"].astype(str)
    return df


def compute_kpi(df: pd.DataFrame) -> pd.DataFrame:
    # KPI per heat: (max energy - min energy) / tons
    g = df.groupby("heat_id", as_index=False).agg(
        start_time=("time", "min"),
        end_time=("time", "max"),
        energy_start=("energy_kwh_total", "min"),
        energy_end=("energy_kwh_total", "max"),
        tons=("tons", "max"),
    )
    g["energy_kwh"] = (g["energy_end"] - g["energy_start"]).round(3)
    g["kwh_per_ton"] = (g["energy_kwh"] / g["tons"]).round(3)
    # keep only meaningful heats (avoid partial)
    g = g[g["energy_kwh"] > 0.1].copy()
    return g.sort_values("heat_id")


def save_plot(kpi: pd.DataFrame, out_path: str = "docs/kpi_kwh_per_ton.png") -> None:
    if kpi.empty:
        return
    x = kpi["heat_id"].tolist()
    y = kpi["kwh_per_ton"].tolist()
    plt.figure()
    plt.plot(x, y, marker="o")
    plt.xlabel("heat_id")
    plt.ylabel("kWh per ton")
    plt.title("EAF KPI: kWh/ton (simulated)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)


def main():
    if not CONFIG.influx_token:
        raise SystemExit("INFLUX_TOKEN is empty. Create .env.example and set INFLUX_TOKEN.")

    client = InfluxDBClient(url=CONFIG.influx_url, token=CONFIG.influx_token, org=CONFIG.influx_org)
    df = query_telemetry(client, lookback_minutes=180)

    if df.empty:
        print("No telemetry found yet. Run simulator + ingestion first.")
        return

    kpi = compute_kpi(df)
    if kpi.empty:
        print("Telemetry exists, but KPI not ready (likely only partial heat data). Wait 1–2 minutes and rerun.")
        return

    # print to console (good evidence screenshot)
    print(kpi[["heat_id", "start_time", "end_time", "tons", "energy_kwh", "kwh_per_ton"]].to_string(index=False))

    # write KPI back to Influx (optional, but nice for dashboards)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for _, row in kpi.iterrows():
        point = {
            "measurement": "kpi_eaf",
            "tags": {"heat_id": str(row["heat_id"])},
            "fields": {
                "energy_kwh": float(row["energy_kwh"]),
                "tons": float(row["tons"]),
                "kwh_per_ton": float(row["kwh_per_ton"]),
            },
            "time": row["end_time"].to_pydatetime(),
        }
        write_api.write(bucket=CONFIG.influx_bucket, record=point)

    save_plot(kpi, out_path="docs/kpi_kwh_per_ton.png")
    print("Saved plot: docs/kpi_kwh_per_ton.png")


if __name__ == "__main__":
    main()
