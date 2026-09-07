from __future__ import annotations

from typing import Any

from backend.app.models.reading import MetricName


VALID_METRICS = {
    "temp_analog_c",
    "temp_digital_c",
    "humidity",
    "aqi",
    "tvoc",
    "eco2",
    "pm1",
    "pm25",
    "pm10",
}


def metric_column(metric: str) -> str:
    """Return an allowlisted sensor column name for a history query."""
    if metric not in VALID_METRICS:
        raise ValueError(f"Unsupported metric: {metric}")
    return metric


class ReadingRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def get_latest(self) -> dict[str, Any] | None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    recorded_at,
                    temp_analog_c,
                    temp_digital_c,
                    humidity,
                    aqi,
                    tvoc,
                    eco2,
                    pm1,
                    pm25,
                    pm10
                FROM sensor_readings
                ORDER BY recorded_at DESC, id DESC
                LIMIT 1
                """
            )
            return cursor.fetchone()

    def get_history(
        self,
        metric: MetricName,
        range_hours: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        column = metric_column(metric)

        # The column cannot be bound as a SQL parameter, so it is interpolated
        # only after validation against the fixed allowlist above.
        sql = f"""
            SELECT recorded_at, value
            FROM (
                SELECT id, recorded_at, {column} AS value
                FROM sensor_readings
                WHERE recorded_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
            ) AS valid_readings
            WHERE value IS NOT NULL
            ORDER BY recorded_at DESC, id DESC
            LIMIT %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(sql, (range_hours, limit))
            rows = cursor.fetchall()

        return list(reversed(rows))

    def get_stats(self, metric: MetricName, range_hours: int) -> dict[str, Any]:
        column = metric_column(metric)
        sql = f"""
            SELECT
                COUNT(value) AS count,
                MIN(value) AS minimum,
                AVG(value) AS average,
                MAX(value) AS maximum
            FROM (
                SELECT {column} AS value
                FROM sensor_readings
                WHERE recorded_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
            ) AS valid_readings
        """
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (range_hours,))
            row = cursor.fetchone()
        return row or {"count": 0, "minimum": None, "average": None, "maximum": None}
