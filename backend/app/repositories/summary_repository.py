from __future__ import annotations

from typing import Any

from backend.app.repositories.reading_repository import ReadingRepository, VALID_METRICS
from backend.app.repositories.settings_repository import SettingsRepository


class SummaryRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def get_context(self, range_hours: int) -> dict[str, Any]:
        readings = ReadingRepository(self.connection)
        indoor = {
            metric: readings.get_stats(metric, range_hours)
            for metric in sorted(VALID_METRICS)
        }
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(state = 1), 0) AS on_count,
                    COALESCE(SUM(state = 1 AND trigger_mode = 'automatic'), 0)
                        AS automatic_on_count,
                    COALESCE(SUM(state = 1 AND trigger_mode = 'manual'), 0)
                        AS manual_on_count,
                    MAX(occurred_at) AS latest_alert_at
                FROM alert_events
                WHERE occurred_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                """,
                (range_hours,),
            )
            alerts = cursor.fetchone() or {}

        return {
            "range_hours": range_hours,
            "indoor": indoor,
            "latest_reading": readings.get_latest(),
            "alerts": alerts,
            "tvoc_threshold": SettingsRepository(self.connection)
                .get_settings()["tvoc_threshold"],
        }
