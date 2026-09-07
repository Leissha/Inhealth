from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class EdgeConfig:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "temperature_db")
    db_user: str = os.getenv("DB_USER", "admin")
    db_password: str = os.getenv("DB_PASSWORD", "")

    serial_port: str = os.getenv("SERIAL_PORT", "")
    serial_baud_rate: int = int(os.getenv("SERIAL_BAUD_RATE", "9600"))
    poll_interval: float = float(os.getenv("SAMPLE_INTERVAL", "0.5"))


def get_edge_config() -> EdgeConfig:
    return EdgeConfig()
