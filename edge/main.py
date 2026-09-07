from __future__ import annotations

import logging
import signal
import time
from dataclasses import dataclass
from typing import Any

from edge.analytics import compute_desired_alert
from edge.config import get_edge_config
from edge.reading_repository import EdgeReadingRepository
from edge.sensor_parser import parse_sensor_line
from edge.serial_client import SerialClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("inhealth.edge")


@dataclass
class EdgeRuntimeState:
    """Small set of values that must survive between poll-loop iterations."""

    last_alert_state: bool | None = None
    last_known_tvoc: int | float | None = None
    last_reading_time: float = 0.0
    previous_connection: Any = None


def handle_serial_line(
    line: str,
    repository: EdgeReadingRepository,
    state: EdgeRuntimeState,
) -> None:
    """Log device messages and save one valid sensor frame."""
    if line.startswith("ACK="):
        logger.info("Arduino acknowledgement: %s", line)
        return

    if line == "Sensors initialised":
        state.last_alert_state = None
        return

    reading = parse_sensor_line(line)
    if reading is None:
        return

    repository.save_reading(reading)
    state.last_known_tvoc = reading.get("tvoc")
    if state.last_reading_time == 0.0:
        logger.info("Database insert succeeded; ingestion started. Serial sample: %s", line)
    state.last_reading_time = time.monotonic()
    logger.debug("Saved reading: %s", reading)


def expire_stale_reading(state: EdgeRuntimeState, now: float | None = None) -> None:
    """Stop an old TVOC value from controlling the current alert state."""
    current_time = time.monotonic() if now is None else now
    if current_time - state.last_reading_time > 15:
        state.last_known_tvoc = None


def update_alert_state(
    settings: tuple[float, bool, bool],
    serial_client: SerialClient,
    state: EdgeRuntimeState,
    repository: EdgeReadingRepository | None = None,
) -> None:
    """Resolve the requested alert and send it only when the state changes."""
    tvoc_threshold, manual_override, manual_alert_enabled = settings
    desired_alert = compute_desired_alert(
        manual_override=manual_override,
        manual_alert_enabled=manual_alert_enabled,
        tvoc=state.last_known_tvoc,
        tvoc_threshold=tvoc_threshold,
    )

    if desired_alert == state.last_alert_state:
        return

    logger.info(
        "Alert state changed: %s -> %s (manual_override=%s, tvoc=%s, thresh=%s)",
        state.last_alert_state,
        desired_alert,
        manual_override,
        state.last_known_tvoc,
        tvoc_threshold,
    )
    if serial_client.set_alert(desired_alert):
        state.last_alert_state = desired_alert
        if repository is not None:
            repository.save_alert_event(
                state=desired_alert,
                trigger_mode="manual" if manual_override else "automatic",
                tvoc_value=state.last_known_tvoc,
                tvoc_threshold=tvoc_threshold,
            )


def run_edge_service() -> None:
    config = get_edge_config()
    repository = EdgeReadingRepository(config)
    serial_client = SerialClient(
        port=config.serial_port,
        baud_rate=config.serial_baud_rate,
    )

    running = True

    def handle_shutdown(signum: int, frame: object) -> None:
        nonlocal running
        logger.info("Received termination signal. Shutting down edge service...")
        running = False

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    state = EdgeRuntimeState()

    logger.info("Starting Inhealth Edge Ingestion & Analytics Service...")
    logger.info("Database target: %s:%s/%s; serial=%s @ %s baud",
                config.db_host, config.db_port, config.db_name,
                config.serial_port or "auto-detect", config.serial_baud_rate)

    while running:
        try:
            line = serial_client.read_line()
            if serial_client.connection is not state.previous_connection:
                state.last_alert_state = None
                state.last_known_tvoc = None
                state.previous_connection = serial_client.connection
            if line:
                handle_serial_line(line, repository, state)

            expire_stale_reading(state)
            settings = repository.get_control_settings()
            update_alert_state(settings, serial_client, state, repository)

            time.sleep(config.poll_interval)
        except Exception as err:
            logger.error("Unexpected error in edge main loop: %s", err)
            time.sleep(1.0)

    serial_client.close()
    logger.info("Edge service gracefully terminated.")


if __name__ == "__main__":
    run_edge_service()
