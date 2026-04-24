import pytest

from simulator.rules import calculate_operating_point


def test_base_compressor_runs_without_compressor_2_for_low_demand():
    point = calculate_operating_point(
        compressed_air_demand=50.0,
        pressure_setpoint=7.0,
    )

    assert point["compressor_1_state"] == 1
    assert point["compressor_2_state"] == 0
    assert point["compressor_2_load_level"] == 0.0
    assert point["active_compressors_count"] == 1
    assert point["total_airflow"] > 0
    assert point["SEC"] > 0


def test_compressor_2_activates_above_base_capacity():
    point = calculate_operating_point(
        compressed_air_demand=80.0,
        pressure_setpoint=7.0,
    )

    assert point["compressor_1_state"] == 1
    assert point["compressor_2_state"] == 1
    assert 40.0 <= point["compressor_2_load_level"] <= 100.0
    assert point["active_compressors_count"] == 2
    assert point["total_airflow"] > 60.0
    assert point["SEC"] > 0


def test_compressor_2_load_is_capped_at_100_percent():
    point = calculate_operating_point(
        compressed_air_demand=120.0,
        pressure_setpoint=7.0,
    )

    assert point["compressor_2_state"] == 1
    assert point["compressor_2_load_level"] == 100.0
    assert point["active_compressors_count"] == 2
    assert point["SEC"] > 0


def test_compressor_2_load_uses_minimum_when_just_above_base_capacity():
    point = calculate_operating_point(
        compressed_air_demand=61.0,
        pressure_setpoint=7.0,
    )

    assert point["compressor_2_state"] == 1
    assert point["compressor_2_load_level"] == 40.0
    assert point["active_compressors_count"] == 2
    assert point["SEC"] > 0


def test_invalid_demand_is_rejected():
    with pytest.raises(ValueError, match="compressed_air_demand"):
        calculate_operating_point(
            compressed_air_demand=0.0,
            pressure_setpoint=7.0,
        )
