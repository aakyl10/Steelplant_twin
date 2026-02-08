import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    mqtt_host: str = os.getenv("MQTT_HOST", "localhost")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_topic: str = os.getenv("MQTT_TOPIC", "steelplant/eaf01/telemetry")

    influx_url: str = os.getenv("INFLUX_URL", "http://localhost:8086")
    influx_org: str = os.getenv("INFLUX_ORG", "steelplant")
    influx_bucket: str = os.getenv("INFLUX_BUCKET", "telemetry")
    influx_token: str = os.getenv("INFLUX_TOKEN", "")

    # NOTE: if you harden MQTT with username/password later, add env vars and use them here.

CONFIG = Config()
