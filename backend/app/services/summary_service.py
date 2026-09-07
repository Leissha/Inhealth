from __future__ import annotations

import json
import time
from datetime import date, datetime
from decimal import Decimal
from statistics import mean
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

from backend.app.models.summary import SummaryResponse


SYSTEM_INSTRUCTION = """
You are the reporting assistant for Inhealth, a local student indoor-air-quality IoT prototype.

Summarise only the supplied structured data. Do not invent measurements, alert events, causes, trends or health diagnoses. Inhealth is not a certified safety or medical device. ENS160 eCO2 is an estimated equivalent CO2 value, not a direct CO2 measurement.

Outdoor Open-Meteo values are modelled regional context for Hawthorn and must not be described as calibration, ground truth, or measurements from the same indoor location. Compare indoor and outdoor PM2.5/PM10 only when both are available.

Do not list every metric because the dashboard already shows them. Mention only the most relevant values when they help explain the situation, for example a TVOC peak, PM2.5 average, or alert count.

Use tvoc_rule.maximum_exceeded_threshold exactly. If it is true, state that TVOC exceeded the configured threshold at least once.

Give a practical interpretation:
- If TVOC exceeded the threshold, mention it clearly.
- If indoor PM2.5/PM10 is lower than outdoor, explain that opening windows may not reduce particulates at that time.
- If indoor PM2.5/PM10 is clearly higher than outdoor, suggest ventilation if practical.
- If readings are otherwise unremarkable, say no immediate action is suggested and recommend continued monitoring.
- If a sensor value looks inconsistent or implausible, suggest checking sensor placement or connection.

Use plain text only. Always include units when mentioning a measurement. Use no more than two decimal places.

Write 2-3 concise, factual and friendly sentences:
1. Overall interpretation.
2. Most relevant evidence, including a small number of useful metrics if needed.
3. One practical next step.
"""
USER_INSTRUCTION = """
Summarise the selected Inhealth time range for the user.

Do not repeat all dashboard metrics. Mention only the most useful values needed to explain the situation, such as TVOC, PM2.5/PM10, or alert activity.

Start with a simple operational interpretation, then explain the most relevant evidence, and finish with one practical next step. Do not invent trends, causes, or safety claims.
"""

def _stats(values: list[float | int | None]) -> dict[str, float] | None:
    valid = [float(value) for value in values if value is not None]
    if not valid:
        return None
    return {"minimum": min(valid), "average": mean(valid), "maximum": max(valid)}


def _compact_context(value: Any) -> Any:
    """Keep the model input numeric, readable and deterministic."""
    if isinstance(value, dict):
        return {key: _compact_context(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_compact_context(item) for item in value]
    if isinstance(value, Decimal):
        numeric = float(value)
        return int(numeric) if numeric.is_integer() else round(numeric, 2)
    if isinstance(value, float):
        return round(value, 2)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


class OpenMeteoClient:
    source = "Open-Meteo / CAMS modelled outdoor context for Hawthorn"

    def fetch(self, range_hours: int) -> dict[str, Any] | None:
        params = urlencode({
            "latitude": -37.8199,
            "longitude": 145.0358,
            "hourly": "pm10,pm2_5",
            "timezone": "Australia/Melbourne",
            "past_hours": range_hours,
            "forecast_hours": 1,
        })
        try:
            with urlopen(
                f"https://air-quality-api.open-meteo.com/v1/air-quality?{params}",
                timeout=4,
            ) as response:
                hourly = json.load(response).get("hourly", {})
            return {
                "source": self.source,
                "pm25": _stats(hourly.get("pm2_5", [])[-range_hours:]),
                "pm10": _stats(hourly.get("pm10", [])[-range_hours:]),
            }
        except Exception:
            return None


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, context: dict[str, Any]) -> str:
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{quote(self.model, safe='')}:generateContent?key={quote(self.api_key, safe='')}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
            "contents": [{"role": "user", "parts": [{
                "text": f"{USER_INSTRUCTION}\n\nStructured context:\n{json.dumps(_compact_context(context))}"
            }]}],
            "generationConfig": {
                "maxOutputTokens": 1536,
                "thinkingConfig": {
                    "thinkingLevel": "minimal" if "flash-lite" in self.model else "low"
                },
            },
        }
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                with urlopen(request, timeout=20) as response:
                    result = json.load(response)
                break
            except HTTPError as error:
                if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                    raise
            except (URLError, TimeoutError):
                if attempt == 2:
                    raise
            time.sleep(attempt + 1)
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()


class SummaryService:
    def __init__(self, repository, open_meteo, gemini) -> None:
        self.repository = repository
        self.open_meteo = open_meteo
        self.gemini = gemini

    def generate(self, range_hours: int) -> SummaryResponse:
        context = self.repository.get_context(range_hours)
        sample_count = max(
            (int(stats.get("count") or 0) for stats in context["indoor"].values()),
            default=0,
        )
        if sample_count == 0:
            raise ValueError("No local sensor data is available for the selected time range")

        try:
            outdoor = self.open_meteo.fetch(range_hours)
        except Exception:
            outdoor = None
        context["outdoor"] = outdoor or {"available": False}
        tvoc_stats = context["indoor"].get("tvoc", {})
        tvoc_maximum = tvoc_stats.get("maximum")
        tvoc_threshold = context.get("tvoc_threshold")
        context["tvoc_rule"] = {
            "threshold": tvoc_threshold,
            "maximum": tvoc_maximum,
            "maximum_exceeded_threshold": (
                tvoc_maximum is not None
                and tvoc_threshold is not None
                and tvoc_maximum > tvoc_threshold
            ),
        }
        summary = self.gemini.generate(context)
        alerts = context["alerts"]
        return SummaryResponse.now(
            range_hours=range_hours,
            summary=summary,
            sample_count=sample_count,
            alerts={
                "automatic_on_count": int(alerts.get("automatic_on_count") or 0),
                "manual_on_count": int(alerts.get("manual_on_count") or 0),
            },
            outdoor={"available": outdoor is not None},
        )
