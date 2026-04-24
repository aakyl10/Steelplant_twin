import json

from simulator.generator import REQUIRED_TELEMETRY_FIELDS, generate_telemetry
from simulator.publisher import MQTT_TOPIC, build_payload, publish_telemetry


class FakePublishResult:
    def __init__(self):
        self.waited = False

    def wait_for_publish(self):
        self.waited = True


class FakeMqttClient:
    def __init__(self):
        self.connected = None
        self.disconnected = False
        self.messages = []
        self.results = []

    def connect(self, host, port):
        self.connected = (host, port)

    def publish(self, topic, payload):
        result = FakePublishResult()
        self.messages.append((topic, payload))
        self.results.append(result)
        return result

    def disconnect(self):
        self.disconnected = True


def test_build_payload_includes_only_required_fields():
    row = generate_telemetry(days=1)[:1][0]
    payload = json.loads(build_payload(row))

    assert set(payload) == set(REQUIRED_TELEMETRY_FIELDS)
    assert "inefficient_scenario" not in payload


def test_publish_telemetry_uses_generated_payload_and_topic():
    rows = generate_telemetry(days=1)[:3]
    client = FakeMqttClient()

    published_count = publish_telemetry(rows=rows, client=client)

    assert published_count == 3
    assert client.connected == ("localhost", 1883)
    assert client.disconnected is True
    assert all(topic == MQTT_TOPIC for topic, _payload in client.messages)
    assert all(result.waited for result in client.results)

    for _topic, payload in client.messages:
        decoded_payload = json.loads(payload)
        assert set(decoded_payload) == set(REQUIRED_TELEMETRY_FIELDS)
        assert "inefficient_scenario" not in decoded_payload
