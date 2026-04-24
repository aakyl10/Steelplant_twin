from simulator.generator import EXPECTED_ROW_COUNT, REQUIRED_TELEMETRY_FIELDS, generate_telemetry


def test_generator_produces_expected_row_count():
    rows = generate_telemetry()

    assert len(rows) == EXPECTED_ROW_COUNT


def test_all_required_fields_exist_in_each_row():
    rows = generate_telemetry()

    for row in rows:
        for field in REQUIRED_TELEMETRY_FIELDS:
            assert field in row


def test_timestamps_are_unique():
    rows = generate_telemetry()
    timestamps = [row["timestamp"] for row in rows]

    assert len(timestamps) == len(set(timestamps))


def test_compressor_2_load_matches_state():
    rows = generate_telemetry()

    for row in rows:
        if row["compressor_2_state"] == 0:
            assert row["compressor_2_load_level"] == 0
        else:
            assert 40 <= row["compressor_2_load_level"] <= 100


def test_sec_is_positive_for_every_row():
    rows = generate_telemetry()

    assert all(row["SEC"] > 0 for row in rows)


def test_inefficient_scenario_period_exists():
    rows = generate_telemetry()
    inefficient_rows = [row for row in rows if row["inefficient_scenario"]]

    assert inefficient_rows
