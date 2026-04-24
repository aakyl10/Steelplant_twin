"""MQTT subscriber that writes telemetry payloads to InfluxDB."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision

from simulator.generator import REQUIRED_TELEMETRY_FIELDS
from simulator.publisher import MQTT_HOST, MQTT_PORT, MQTT_TOPIC

MEASUREMENT_NAME = "compressed_air_telemetry"
NUMERIC_TELEMETRY_FIELDS = tuple(
    field for field in REQUIRED_TELEMETRY_FIELDS if field != "timestamp"
)


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp from an MQTT payload."""
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def parse_payload(payload: str | bytes) -> dict[str, Any]:
    """Parse and validate a JSON telemetry payload."""
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    data = json.loads(payload)
    missing_fields = [field for field in REQUIRED_TELEMETRY_FIELDS if field not in data]
    if missing_fields:
        raise ValueError(f"missing required telemetry fields: {missing_fields}")

    return data


def payload_to_point(payload: dict[str, Any]) -> Point:
    """Convert a validated telemetry payload into an InfluxDB point."""
    missing_fields = [field for field in REQUIRED_TELEMETRY_FIELDS if field not in payload]
    if missing_fields:
        raise ValueError(f"missing required telemetry fields: {missing_fields}")

    timestamp = parse_timestamp(str(payload["timestamp"]))
    point = Point(MEASUREMENT_NAME).time(timestamp, WritePrecision.NS)

    for field in NUMERIC_TELEMETRY_FIELDS:
        value = payload[field]
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError(f"{field} must be numeric")
        point.field(field, value)

    return point


def create_mqtt_client() -> Any:
    """Create a paho-mqtt client while supporting paho 1.x and 2.x."""
    import paho.mqtt.client as mqtt

    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        return mqtt.Client()


def write_payload_to_influx(
    payload: str | bytes,
    write_api: Any,
    bucket: str,
    org: str,
) -> Point:
    """Parse one MQTT payload and write it to InfluxDB."""
    data = parse_payload(payload)
    point = payload_to_point(data)
    write_api.write(bucket=bucket, org=org, record=point)
    return point


def build_on_message(write_api: Any, bucket: str, org: str):
    """Create an MQTT message callback that writes payloads to InfluxDB."""

    def on_message(_client: Any, _userdata: Any, message: Any) -> None:
        write_payload_to_influx(message.payload, write_api=write_api, bucket=bucket, org=org)

    return on_message


def run_ingestion() -> None:
    """Subscribe to MQTT telemetry and write messages to InfluxDB."""
    load_dotenv()

    influx_url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    influx_org = os.getenv("INFLUXDB_ORG", "steelplant")
    influx_bucket = os.getenv("INFLUXDB_BUCKET", "telemetry")
    influx_token = os.getenv("INFLUXDB_TOKEN")
    if not influx_token:
        raise RuntimeError("INFLUXDB_TOKEN environment variable is required")

    mqtt_host = os.getenv("MQTT_HOST", MQTT_HOST)
    mqtt_port = int(os.getenv("MQTT_PORT", str(MQTT_PORT)))
    mqtt_topic = os.getenv("MQTT_TOPIC", MQTT_TOPIC)

    with InfluxDBClient(
        url=influx_url,
        token=influx_token,
        org=influx_org,
    ) as influx_client:
        write_api = influx_client.write_api()
        mqtt_client = create_mqtt_client()
        mqtt_client.on_message = build_on_message(
            write_api=write_api,
            bucket=influx_bucket,
            org=influx_org,
        )
        mqtt_client.connect(mqtt_host, mqtt_port)
        mqtt_client.subscribe(mqtt_topic)
        print(f"Subscribed to {mqtt_topic}; writing to InfluxDB bucket {influx_bucket}")
        mqtt_client.loop_forever()


def main() -> None:
    """Run ingestion from the command line."""
    run_ingestion()


if __name__ == "__main__":
    main()
