"""Rule-based compressor logic for the virtual compressed-air plant."""

BASE_COMPRESSOR_CAPACITY = 60.0
SECONDARY_COMPRESSOR_CAPACITY = 40.0
BASE_COMPRESSOR_POWER = 7.0
SECONDARY_COMPRESSOR_POWER = 5.0
MIN_COMPRESSOR_2_LOAD = 40.0
MAX_COMPRESSOR_2_LOAD = 100.0


def calculate_compressor_2_load(
    demand: float,
    base_capacity: float = BASE_COMPRESSOR_CAPACITY,
    secondary_capacity: float = SECONDARY_COMPRESSOR_CAPACITY,
) -> float:
    """Return compressor 2 load percentage for the given demand."""
    if demand <= base_capacity:
        return 0.0

    required_load = ((demand - base_capacity) / secondary_capacity) * 100.0
    return max(MIN_COMPRESSOR_2_LOAD, min(required_load, MAX_COMPRESSOR_2_LOAD))


def calculate_sec(
    total_airflow: float,
    compressor_2_load_level: float,
    pressure_setpoint: float,
    pressure_deviation: float,
    inefficient: bool = False,
) -> float:
    """Calculate positive Specific Energy Consumption from airflow and load."""
    if total_airflow <= 0:
        raise ValueError("total_airflow must be positive")
    if pressure_setpoint <= 0:
        raise ValueError("pressure_setpoint must be positive")

    compressor_2_power = SECONDARY_COMPRESSOR_POWER * (compressor_2_load_level / 100.0)
    pressure_factor = 1.0 + max(pressure_setpoint - 7.0, 0.0) * 0.04
    deviation_factor = 1.0 + abs(pressure_deviation) * 0.03
    inefficiency_factor = 1.15 if inefficient else 1.0

    power = (BASE_COMPRESSOR_POWER + compressor_2_power) * pressure_factor
    sec = (power * deviation_factor * inefficiency_factor) / total_airflow
    return round(sec, 6)


def calculate_operating_point(
    compressed_air_demand: float,
    pressure_setpoint: float,
    pressure_deviation: float = 0.0,
    inefficient: bool = False,
) -> dict[str, float | int]:
    """Calculate compressor states, airflow, and SEC for one telemetry step."""
    if compressed_air_demand <= 0:
        raise ValueError("compressed_air_demand must be positive")

    compressor_1_state = 1
    compressor_2_load_level = calculate_compressor_2_load(compressed_air_demand)
    compressor_2_state = int(compressor_2_load_level > 0)
    active_compressors_count = compressor_1_state + compressor_2_state

    total_airflow = BASE_COMPRESSOR_CAPACITY
    if compressor_2_state:
        total_airflow += SECONDARY_COMPRESSOR_CAPACITY * (
            compressor_2_load_level / 100.0
        )

    sec = calculate_sec(
        total_airflow=total_airflow,
        compressor_2_load_level=compressor_2_load_level,
        pressure_setpoint=pressure_setpoint,
        pressure_deviation=pressure_deviation,
        inefficient=inefficient,
    )

    return {
        "compressor_1_state": compressor_1_state,
        "compressor_2_state": compressor_2_state,
        "compressor_2_load_level": round(compressor_2_load_level, 3),
        "active_compressors_count": active_compressors_count,
        "total_airflow": round(total_airflow, 3),
        "pressure_deviation": pressure_deviation,
        "SEC": sec,
    }
