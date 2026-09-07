from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SettingsResponse(BaseModel):
    """Control settings currently used by the edge service."""

    model_config = ConfigDict(from_attributes=True)

    tvoc_threshold: float = Field(ge=0.0, le=10000.0)
    manual_override: bool = False
    manual_alert_enabled: bool = False


class TvocThresholdUpdate(BaseModel):
    value: float = Field(
        ...,
        ge=0.0,
        le=10000.0,
        description="TVOC threshold in parts per billion (ppb).",
    )


class ActuatorAlertRequest(BaseModel):
    enabled: bool


class ActuatorAlertResponse(BaseModel):
    accepted: bool
    manual_override: bool
    requested_alert: bool
    message: str


class DeviceStatusResponse(BaseModel):
    edge_api: str = "online"
    arduino_connected: bool
    serial_port: Optional[str] = None
    baud_rate: int = 9600
    last_reading_at: Optional[datetime] = None
