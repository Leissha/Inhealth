from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from backend.app.api.readings import get_reading_repository
from backend.app.config import Settings, get_settings
from backend.app.models.controls import DeviceStatusResponse
from backend.app.repositories.reading_repository import ReadingRepository


router = APIRouter(prefix="/api/device", tags=["device"])


ReadingRepoDependency = Annotated[
    ReadingRepository,
    Depends(get_reading_repository),
]
ConfigDependency = Annotated[
    Settings,
    Depends(get_settings),
]


@router.get("/status", response_model=DeviceStatusResponse)
def get_device_status(
    reading_repo: ReadingRepoDependency,
    config: ConfigDependency,
) -> DeviceStatusResponse:
    latest = reading_repo.get_latest()
    last_reading_at: datetime | None = None
    arduino_connected = False

    if latest is not None and "recorded_at" in latest:
        raw_recorded_at = latest["recorded_at"]
        if isinstance(raw_recorded_at, datetime):
            last_reading_at = raw_recorded_at
        elif isinstance(raw_recorded_at, str):
            try:
                last_reading_at = datetime.fromisoformat(raw_recorded_at)
            except ValueError:
                pass

        if last_reading_at is not None:
            now = datetime.now(timezone.utc) if last_reading_at.tzinfo else datetime.now()
            delta_seconds = abs((now - last_reading_at).total_seconds())
            # Consider connected if reading is within 15 seconds
            arduino_connected = delta_seconds <= 15.0

    serial_port = config.serial_port if config.serial_port.strip() else None

    return DeviceStatusResponse(
        edge_api="online",
        arduino_connected=arduino_connected,
        serial_port=serial_port,
        baud_rate=config.serial_baud_rate,
        last_reading_at=last_reading_at,
    )
