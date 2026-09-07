from __future__ import annotations

from typing import Any
import pymysql
from pymysql.cursors import DictCursor

from edge.config import EdgeConfig


class EdgeReadingRepository:
    def __init__(self, config: EdgeConfig) -> None:
        self.config = config

    def _get_connection(self) -> Any:
        return pymysql.connect(
            host=self.config.db_host,
            port=self.config.db_port,
            user=self.config.db_user,
            password=self.config.db_password,
            database=self.config.db_name,
            cursorclass=DictCursor,
            autocommit=True,
            connect_timeout=5,
        )

    def save_reading(self, reading: dict[str, Any]) -> None:
        sql = """
            INSERT INTO sensor_readings (temp_analog_c, temp_digital_c, humidity, aqi, tvoc, eco2, pm1, pm25, pm10) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            reading.get("temp_analog_c"), reading.get("temp_digital_c"), reading.get("humidity"), reading.get("aqi"), reading.get("tvoc"), reading.get("eco2"), reading.get("pm1"), reading.get("pm25"), reading.get("pm10")
        )
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
        finally:
            conn.close()

    def save_alert_event(
        self,
        state: bool,
        trigger_mode: str,
        tvoc_value: int | float | None,
        tvoc_threshold: float | None,
    ) -> None:
        sql = """
            INSERT INTO alert_events
                (state, trigger_mode, tvoc_value, tvoc_threshold)
            VALUES (%s, %s, %s, %s)
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    sql,
                    (state, trigger_mode, tvoc_value, tvoc_threshold),
                )
        finally:
            conn.close()

    def get_control_settings(self) -> tuple[float, bool, bool]:
        """
        Returns (tvoc_threshold, manual_override, manual_alert_enabled).
        Defaults to (100.0, False, False) if table is inaccessible or values missing.
        """
        try:
            conn = self._get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT setting_key, setting_value FROM settings")
                    rows = cursor.fetchall()
            finally:
                conn.close()

            settings_map = {row["setting_key"]: row["setting_value"] for row in rows}

            raw_thresh = settings_map.get("tvoc_threshold", "100")
            try:
                tvoc_threshold = float(raw_thresh)
            except (ValueError, TypeError):
                tvoc_threshold = 100.0

            override = settings_map.get("manual_override", "0")
            alert = settings_map.get("manual_alert_enabled", "0")
            manual_override = override == 1 or override in {"1", "true", "True"}
            manual_alert_enabled = alert == 1 or alert in {"1", "true", "True"}

            return tvoc_threshold, manual_override, manual_alert_enabled
        except Exception:
            return 100.0, False, False
