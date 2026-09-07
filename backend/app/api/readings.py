from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.db import get_db_connection
from backend.app.models.reading import MetricName, ReadingHistory, ReadingStats, SensorReading
from backend.app.repositories.reading_repository import ReadingRepository


router = APIRouter(prefix="/api/readings", tags=["readings"])


def get_reading_repository(
    connection: Any = Depends(get_db_connection),
) -> ReadingRepository:
    return ReadingRepository(connection)


RepositoryDependency = Annotated[
    ReadingRepository,
    Depends(get_reading_repository),
]


@router.get("/latest", response_model=SensorReading)
def get_latest_reading(repository: RepositoryDependency) -> SensorReading:
    reading = repository.get_latest()
    if reading is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sensor readings are available",
        )
    return SensorReading.model_validate(reading)


@router.get("/history", response_model=ReadingHistory)
def get_reading_history(
    repository: RepositoryDependency,
    metric: MetricName = "tvoc",
    range_hours: Annotated[int, Query(alias="range", ge=1, le=168)] = 24,
    limit: Annotated[int, Query(ge=1, le=1000)] = 200,
) -> ReadingHistory:
    points = repository.get_history(metric, range_hours, limit)
    return ReadingHistory(metric=metric, points=points)


@router.get("/stats", response_model=ReadingStats)
def get_reading_stats(
    repository: RepositoryDependency,
    metric: MetricName = "tvoc",
    range_hours: Annotated[int, Query(alias="range", ge=1, le=168)] = 24,
) -> ReadingStats:
    stats = repository.get_stats(metric, range_hours)
    return ReadingStats(metric=metric, range=range_hours, **stats)
