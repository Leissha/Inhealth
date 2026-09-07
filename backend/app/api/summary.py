from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.config import get_settings
from backend.app.db import get_db_connection
from backend.app.models.summary import SummaryRequest, SummaryResponse
from backend.app.repositories.summary_repository import SummaryRepository
from backend.app.services.summary_service import GeminiClient, OpenMeteoClient, SummaryService


router = APIRouter(prefix="/api/summary", tags=["summary"])


def get_summary_service(connection: Any = Depends(get_db_connection)) -> SummaryService:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI summary is not configured. Set GEMINI_API_KEY on the edge server.",
        )
    return SummaryService(
        SummaryRepository(connection),
        OpenMeteoClient(),
        GeminiClient(settings.gemini_api_key, settings.gemini_model),
    )


ServiceDependency = Annotated[SummaryService, Depends(get_summary_service)]


@router.post("", response_model=SummaryResponse)
def generate_summary(payload: SummaryRequest, service: ServiceDependency) -> SummaryResponse:
    try:
        return service.generate(payload.range_hours)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="The AI summary could not be generated. Please try again.",
        ) from error
