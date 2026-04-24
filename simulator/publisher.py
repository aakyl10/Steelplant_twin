"""MQTT publisher for generated compressed-air telemetry."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterable
from typing import Any

from dotenv import load_dotenv

from simulator.generator import REQUIRED_TELEMETRY_FIELDS, generate_telemetry

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "steelplant/compressed_air/telemetry")


def build_payload(row: dict[str, Any]) -> str:
    """Build a JSON MQTT payload using only required telemetry fields."""
    missing_fields = [field for field in REQUIRED_TELEMETRY_FIELDS if field not in row]
    if missing_fields:
        raise ValueError(f"missing required telemetry fields: {missing_fields}")

    payload = {field: row[field] for field in REQUIRED_TELEMETRY_FIELDS}
    return json.dumps(payload, separators=(",", ":"))


def create_mqtt_client() -> Any:
    """Create a paho-mqtt client while supporting paho 1.x and 2.x."""
    import paho.mqtt.client as mqtt

    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        return mqtt.Client()


def publish_telemetry(
    rows: Iterable[dict[str, Any]] | None = None,
    host: str = MQTT_HOST,
    port: int = MQTT_PORT,
    topic: str = MQTT_TOPIC,
    delay_seconds: float = 0.0,
    client: Any | None = None,
) -> int:
    """Publish telemetry rows as JSON MQTT messages."""
    telemetry_rows = generate_telemetry() if rows is None else rows
    mqtt_client = create_mqtt_client() if client is None else client
    published_count = 0

    mqtt_client.connect(host, port)

    try:
        for row in telemetry_rows:
            payload = build_payload(row)
            publish_result = mqtt_client.publish(topic, payload)
            wait_for_publish = getattr(publish_result, "wait_for_publish", None)
            if wait_for_publish is not None:
                wait_for_publish()
            published_count += 1

            if delay_seconds > 0:
                time.sleep(delay_seconds)
    finally:
        mqtt_client.disconnect()

    return published_count


def main() -> None:
    """Run the MQTT publisher from the command line."""
    published_count = publish_telemetry()
    print(f"Published {published_count} telemetry messages to {MQTT_TOPIC}")


if __name__ == "__main__":
    main()
