from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


MetricName = Literal[
    "temp_analog_c",
    "temp_digital_c",
    "humidity",
    "aqi",
    "tvoc",
    "eco2",
    "pm1",
    "pm25",
    "pm10",
]


class SensorReading(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recorded_at: datetime
    temp_analog_c: Optional[float] = None
    temp_digital_c: Optional[float] = None
    humidity: Optional[float] = None
    aqi: Optional[int] = Field(default=None, ge=1, le=5)
    tvoc: Optional[int] = Field(default=None, ge=0)
    eco2: Optional[int] = Field(default=None, ge=0)
    pm1: Optional[float] = Field(default=None, ge=0)
    pm25: Optional[float] = Field(default=None, ge=0)
    pm10: Optional[float] = Field(default=None, ge=0)


class HistoryPoint(BaseModel):
    recorded_at: datetime
    value: Union[float, int]


class ReadingHistory(BaseModel):
    metric: MetricName
    points: list[HistoryPoint]


class ReadingStats(BaseModel):
    metric: MetricName
    range: int = Field(ge=1, le=168)
    count: int = Field(ge=0)
    minimum: Optional[float] = None
    average: Optional[float] = None
    maximum: Optional[float] = None
