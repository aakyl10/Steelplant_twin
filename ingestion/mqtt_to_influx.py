import json
import sys
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from common import CONFIG


REQUIRED_FIELDS = {
    "ts", "device_id", "heat_id", "mode", "power_kw", "energy_kwh_total", "pump_kw", "compressor_kw", "tons"
}

MODE_SET = {"idle", "melt", "refine", "downtime"}


def parse_ts(ts: str) -> datetime:
    # expecting ISO 8601 with timezone (from simulator)
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


def validate(payload: dict) -> None:
    missing = REQUIRED_FIELDS - set(payload.keys())
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")

    if payload["mode"] not in MODE_SET:
        raise ValueError(f"Invalid mode: {payload['mode']}")
    # basic range checks (anti-garbage; also supports security narrative)
    if not (0 <= float(payload["power_kw"]) <= 6000):
        raise ValueError("power_kw out of expected range")
    if not (0 <= float(payload["pump_kw"]) <= 500):
        raise ValueError("pump_kw out of expected range")
    if not (0 <= float(payload["compressor_kw"]) <= 500):
        raise ValueError("compressor_kw out of expected range")
    if not (0 <= float(payload["tons"]) <= 400):
        raise ValueError("tons out of expected range")


def main():
    if not CONFIG.influx_token:
        print("ERROR: INFLUX_TOKEN is empty. Create .env.example and set INFLUX_TOKEN.", file=sys.stderr)
        sys.exit(2)

    influx = InfluxDBClient(url=CONFIG.influx_url, token=CONFIG.influx_token, org=CONFIG.influx_org)
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected to MQTT (reason_code={reason_code}). Subscribing to {CONFIG.mqtt_topic}")
        client.subscribe(CONFIG.mqtt_topic, qos=0)

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            validate(payload)
            ts = parse_ts(payload["ts"])

            p = (
                Point("telemetry_eaf")
                .tag("device_id", str(payload["device_id"]))
                .tag("mode", str(payload["mode"]))
                .tag("heat_id", str(payload["heat_id"]))
                .field("power_kw", float(payload["power_kw"]))
                .field("energy_kwh_total", float(payload["energy_kwh_total"]))
                .field("pump_kw", float(payload["pump_kw"]))
                .field("compressor_kw", float(payload["compressor_kw"]))
                .field("tons", float(payload["tons"]))
                .time(ts, WritePrecision.S)
            )

            write_api.write(bucket=CONFIG.influx_bucket, record=p)
            # lightweight evidence output
            print(f"[INGEST] ts={payload['ts']} heat={payload['heat_id']} mode={payload['mode']} power={payload['power_kw']}kW -> InfluxDB")
        except Exception as e:
            print(f"[DROP] {e}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(CONFIG.mqtt_host, CONFIG.mqtt_port, keepalive=60)
    print(f"MQTT subscribe: mqtt://{CONFIG.mqtt_host}:{CONFIG.mqtt_port} topic='{CONFIG.mqtt_topic}'")
    print(f"Influx target: {CONFIG.influx_url} org='{CONFIG.influx_org}' bucket='{CONFIG.influx_bucket}'")
    print("Press Ctrl+C to stop.")
    client.loop_forever()


if __name__ == "__main__":
    main()
