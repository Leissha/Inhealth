from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    range_hours: Literal[1, 6, 12, 24]


class AlertSummary(BaseModel):
    automatic_on_count: int
    manual_on_count: int


class OutdoorSummary(BaseModel):
    available: bool
    source: str = "Open-Meteo / CAMS"
    location: str = "Hawthorn"


class SummaryResponse(BaseModel):
    range_hours: int
    summary: str
    sample_count: int
    generated_at: datetime
    alerts: AlertSummary
    outdoor: OutdoorSummary

    @classmethod
    def now(cls, **values):
        return cls(generated_at=datetime.now(timezone.utc), **values)
