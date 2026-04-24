"""Telemetry generator for the virtual compressed-air plant."""

from __future__ import annotations

import json
import math
from datetime import UTC, datetime, timedelta

from simulator.rules import calculate_operating_point

SIMULATION_DAYS = 30
INTERVAL_MINUTES = 5
ROWS_PER_HOUR = 60 // INTERVAL_MINUTES
EXPECTED_ROW_COUNT = SIMULATION_DAYS * 24 * ROWS_PER_HOUR
DEFAULT_START_TIME = datetime(2026, 4, 1, tzinfo=UTC)
INEFFICIENT_START_DAY = 14
INEFFICIENT_DURATION_HOURS = 8

REQUIRED_TELEMETRY_FIELDS = (
    "timestamp",
    "ambient_temperature",
    "compressed_air_demand",
    "pressure_setpoint",
    "compressor_1_state",
    "compressor_2_state",
    "compressor_2_load_level",
    "active_compressors_count",
    "total_airflow",
    "pressure_deviation",
    "SEC",
)


def is_inefficient_period(timestamp: datetime, start_time: datetime) -> bool:
    """Return whether the timestamp belongs to the inefficient scenario."""
    inefficient_start = start_time + timedelta(
        days=INEFFICIENT_START_DAY,
        hours=8,
    )
    inefficient_end = inefficient_start + timedelta(hours=INEFFICIENT_DURATION_HOURS)
    return inefficient_start <= timestamp < inefficient_end


def generate_demand(step: int) -> float:
    """Create a smooth daily compressed-air demand pattern."""
    steps_per_day = 24 * ROWS_PER_HOUR
    day_step = step % steps_per_day
    day_fraction = day_step / steps_per_day

    daily_wave = math.sin(2.0 * math.pi * (day_fraction - 0.25))
    shift_wave = math.sin(4.0 * math.pi * (day_fraction - 0.32))
    demand = 58.0 + 18.0 * daily_wave + 5.0 * shift_wave
    return round(max(demand, 35.0), 3)


def generate_ambient_temperature(step: int) -> float:
    """Create a smooth daily ambient temperature pattern."""
    steps_per_day = 24 * ROWS_PER_HOUR
    day_fraction = (step % steps_per_day) / steps_per_day
    temperature = 22.0 + 6.0 * math.sin(2.0 * math.pi * (day_fraction - 0.35))
    return round(temperature, 3)


def generate_pressure_deviation(step: int, inefficient: bool) -> float:
    """Create a small smooth pressure deviation, larger during inefficiency."""
    steps_per_day = 24 * ROWS_PER_HOUR
    day_fraction = (step % steps_per_day) / steps_per_day
    deviation = 0.08 * math.sin(2.0 * math.pi * day_fraction)
    if inefficient:
        deviation += 0.35
    return round(deviation, 3)


def generate_telemetry(
    start_time: datetime = DEFAULT_START_TIME,
    days: int = SIMULATION_DAYS,
    interval_minutes: int = INTERVAL_MINUTES,
) -> list[dict[str, float | int | str | bool]]:
    """Generate telemetry rows that follow the project data contract."""
    row_count = days * 24 * (60 // interval_minutes)
    rows = []

    for step in range(row_count):
        timestamp = start_time + timedelta(minutes=step * interval_minutes)
        inefficient = is_inefficient_period(timestamp, start_time)
        demand = generate_demand(step)
        ambient_temperature = generate_ambient_temperature(step)
        pressure_setpoint = 7.4 if inefficient else 7.0
        pressure_deviation = generate_pressure_deviation(step, inefficient)

        operating_point = calculate_operating_point(
            compressed_air_demand=demand,
            pressure_setpoint=pressure_setpoint,
            pressure_deviation=pressure_deviation,
            inefficient=inefficient,
        )

        row = {
            "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
            "ambient_temperature": ambient_temperature,
            "compressed_air_demand": demand,
            "pressure_setpoint": pressure_setpoint,
            **operating_point,
            "inefficient_scenario": inefficient,
        }
        rows.append(row)

    return rows


def main() -> None:
    """Run the generator from the command line."""
    rows = generate_telemetry()
    inefficient_rows = sum(1 for row in rows if row["inefficient_scenario"])
    summary = {
        "rows": len(rows),
        "start": rows[0]["timestamp"],
        "end": rows[-1]["timestamp"],
        "inefficient_rows": inefficient_rows,
        "fields": list(REQUIRED_TELEMETRY_FIELDS),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
