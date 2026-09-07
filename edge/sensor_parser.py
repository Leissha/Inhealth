from __future__ import annotations

from math import isfinite
from typing import Any


READING_FIELDS = {
    "TEMP_ANALOG_C": ("temp_analog_c", float),
    "TEMP_DIGITAL_C": ("temp_digital_c", float),
    "HUMIDITY": ("humidity", float),
    "AQI": ("aqi", int),
    "TVOC": ("tvoc", int),
    "ECO2": ("eco2", int),
    "PM1": ("pm1", float),
    "PM25": ("pm25", float),
    "PM2.5": ("pm25", float),
    "PM10": ("pm10", float),
}

# Current firmware keeps the frame shape stable. A missing PM sample is sent as
# NULL values rather than by removing the particle fields.
REQUIRED_FRAME_KEYS = {
    "TEMP_ANALOG_C",
    "AQI",
    "TVOC",
    "ECO2",
    "PM1",
    "PM25",
    "PM10",
}


def is_non_reading_message(line: str) -> bool:
    """Return True for empty, status and acknowledgement messages."""
    cleaned = line.strip()
    return (
        not cleaned
        or cleaned.startswith("ACK=")
        or cleaned.startswith("Sensors ")
        or "begin failed" in cleaned
        or "not found" in cleaned
        or "=" not in cleaned
    )


def parse_value(key: str, value: str) -> tuple[str, int | float | None] | None:
    """Convert one known firmware field to its Python name and value."""
    field = READING_FIELDS.get(key)
    if field is None:
        return None

    field_name, converter = field
    if value.upper() == "NULL":
        return field_name, None

    try:
        return field_name, converter(value)
    except (TypeError, ValueError):
        return field_name, None


def parse_tokens(line: str) -> tuple[dict[str, Any], set[str]] | None:
    """Split a complete serial line and convert all recognised fields."""
    tokens = [token.strip() for token in line.split(",") if token.strip()]
    if not tokens or any("=" not in token for token in tokens):
        return None

    reading = {field_name: None for field_name, _ in READING_FIELDS.values()}
    frame_keys: set[str] = set()

    for token in tokens:
        raw_key, _, raw_value = token.partition("=")
        key = raw_key.strip().upper()
        value = raw_value.strip()
        if not value:
            return None

        frame_keys.add(key)
        if key == "PM2.5":
            frame_keys.add("PM25")
        parsed = parse_value(key, value)
        if parsed is not None:
            field_name, parsed_value = parsed
            reading[field_name] = parsed_value

    return reading, frame_keys


def normalize_reading(reading: dict[str, Any]) -> dict[str, Any] | None:
    """Apply sensor-range rules and return a database-ready reading."""
    aqi = reading["aqi"]
    if aqi is not None and not 1 <= aqi <= 5:
        reading["aqi"] = None

    # The ENS160 produces this exact triplet when its header loses contact.
    if reading["aqi"] is None and reading["tvoc"] == 0 and reading["eco2"] == 0:
        reading["tvoc"] = None
        reading["eco2"] = None

    for key, value in reading.items():
        if value is None:
            continue
        invalid = not isfinite(value)
        invalid |= key not in {"temp_analog_c", "temp_digital_c"} and value < 0
        invalid |= key == "humidity" and value > 100
        if invalid:
            reading[key] = None

    return reading if any(value is not None for value in reading.values()) else None


def parse_sensor_line(line: str) -> dict[str, Any] | None:
    """Convert one current-firmware serial frame into a clean reading."""
    if is_non_reading_message(line):
        return None

    parsed = parse_tokens(line.strip())
    if parsed is None:
        return None

    reading, frame_keys = parsed
    if not REQUIRED_FRAME_KEYS.issubset(frame_keys):
        return None

    return normalize_reading(reading)
