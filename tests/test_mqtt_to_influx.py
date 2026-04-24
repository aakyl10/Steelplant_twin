import json
from datetime import UTC, datetime

import pytest
from influxdb_client import Point

from ingestion.mqtt_to_influx import (
    MEASUREMENT_NAME,
    NUMERIC_TELEMETRY_FIELDS,
    build_on_message,
    handle_message_payload,
    parse_payload,
    parse_timestamp,
    payload_to_point,
    write_payload_to_influx,
)
from simulator.generator import REQUIRED_TELEMETRY_FIELDS


class FakeWriteApi:
    def __init__(self):
        self.calls = []

    def write(self, bucket, org, record):
        self.calls.append({"bucket": bucket, "org": org, "record": record})


class FakeMqttMessage:
    def __init__(self, payload):
        self.payload = payload


def valid_payload():
    return {
        "timestamp": "2026-04-24T10:00:00Z",
        "ambient_temperature": 24.5,
        "compressed_air_demand": 72.3,
        "pressure_setpoint": 7.0,
        "compressor_1_state": 1,
        "compressor_2_state": 1,
        "compressor_2_load_level": 55.0,
        "active_compressors_count": 2,
        "total_airflow": 75.0,
        "pressure_deviation": 0.12,
        "SEC": 0.118,
    }


def test_valid_mqtt_payload_is_written_as_influx_point():
    write_api = FakeWriteApi()
    payload = json.dumps(valid_payload())

    point = write_payload_to_influx(
        payload,
        write_api=write_api,
        bucket="telemetry",
        org="steelplant",
    )

    assert isinstance(point, Point)
    assert write_api.calls == [
        {"bucket": "telemetry", "org": "steelplant", "record": point}
    ]
    assert point.to_line_protocol().startswith(MEASUREMENT_NAME)


def test_missing_required_fields_are_rejected():
    payload = valid_payload()
    del payload["SEC"]

    with pytest.raises(ValueError, match="missing required telemetry fields"):
        parse_payload(json.dumps(payload))


def test_timestamp_is_parsed_as_utc_datetime():
    parsed = parse_timestamp("2026-04-24T10:00:00Z")

    assert parsed == datetime(2026, 4, 24, 10, 0, tzinfo=UTC)


def test_numeric_telemetry_fields_are_preserved():
    payload = valid_payload()
    point = payload_to_point(payload)

    assert set(point._fields) == set(NUMERIC_TELEMETRY_FIELDS)
    for field in NUMERIC_TELEMETRY_FIELDS:
        assert point._fields[field] == payload[field]


def test_simulation_only_fields_are_not_required_or_stored():
    payload = valid_payload()
    payload["inefficient_scenario"] = True

    point = payload_to_point(parse_payload(json.dumps(payload)))

    assert set(REQUIRED_TELEMETRY_FIELDS).issubset(payload)
    assert "inefficient_scenario" not in point._fields


def test_invalid_message_payload_is_rejected_without_write():
    write_api = FakeWriteApi()

    point = handle_message_payload(
        b"{not-json",
        write_api=write_api,
        bucket="telemetry",
        org="steelplant",
    )

    assert point is None
    assert write_api.calls == []


def test_on_message_callback_does_not_raise_for_missing_fields():
    write_api = FakeWriteApi()
    payload = valid_payload()
    del payload["SEC"]
    callback = build_on_message(write_api=write_api, bucket="telemetry", org="steelplant")

    callback(None, None, FakeMqttMessage(json.dumps(payload).encode("utf-8")))

    assert write_api.calls == []
