from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from backend.app.api.settings import get_settings_repository
from backend.app.models.controls import ActuatorAlertRequest, ActuatorAlertResponse
from backend.app.repositories.settings_repository import SettingsRepository


router = APIRouter(prefix="/api/actuators", tags=["actuators"])


SettingsRepoDependency = Annotated[
    SettingsRepository,
    Depends(get_settings_repository),
]


@router.post("/alert", response_model=ActuatorAlertResponse)
def set_actuator_alert(
    payload: ActuatorAlertRequest,
    repository: SettingsRepoDependency,
) -> ActuatorAlertResponse:
    override, alert_enabled = repository.set_manual_override(payload.enabled)

    if payload.enabled:
        message = "Alert test requested. Manual override active."
    else:
        message = "Alert test stopped. Resuming automatic threshold evaluation."

    return ActuatorAlertResponse(
        accepted=True,
        manual_override=override,
        requested_alert=alert_enabled,
        message=message,
    )
