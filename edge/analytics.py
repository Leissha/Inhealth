from __future__ import annotations

def compute_desired_alert(
    manual_override: bool,
    manual_alert_enabled: bool,
    tvoc: int | float | None,
    tvoc_threshold: float,
) -> bool:
    """
    Evaluates the effective alert state for the actuator:
    1. Manual override takes absolute precedence (for testing / manual control).
    2. If manual override is inactive, automatic threshold logic applies.
    3. If TVOC is None (missing/corrupt), returns False to prevent false alarms.
    """
    if manual_override:
        return manual_alert_enabled

    if tvoc is None:
        return False

    return tvoc > tvoc_threshold
