from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from backend.app.db import get_db_connection
from backend.app.models.controls import SettingsResponse, TvocThresholdUpdate
from backend.app.repositories.settings_repository import SettingsRepository


router = APIRouter(prefix="/api/settings", tags=["settings"])


def get_settings_repository(
    connection: Any = Depends(get_db_connection),
) -> SettingsRepository:
    return SettingsRepository(connection)


SettingsRepoDependency = Annotated[
    SettingsRepository,
    Depends(get_settings_repository),
]


@router.get("", response_model=SettingsResponse)
def get_settings(repository: SettingsRepoDependency) -> SettingsResponse:
    settings_data = repository.get_settings()
    return SettingsResponse.model_validate(settings_data)


@router.put("/tvoc-threshold", response_model=SettingsResponse)
def update_tvoc_threshold(
    payload: TvocThresholdUpdate,
    repository: SettingsRepoDependency,
) -> SettingsResponse:
    repository.update_tvoc_threshold(payload.value)
    updated_settings = repository.get_settings()
    return SettingsResponse.model_validate(updated_settings)
