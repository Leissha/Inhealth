from __future__ import annotations

from typing import Any


class SettingsRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def get_settings(self) -> dict[str, Any]:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT setting_key, setting_value FROM settings")
            rows = cursor.fetchall()

        settings_map: dict[str, str] = {}
        for row in rows:
            settings_map[row["setting_key"]] = row["setting_value"]

        raw_threshold = settings_map.get("tvoc_threshold", "100")
        try:
            tvoc_threshold = float(raw_threshold)
        except (ValueError, TypeError):
            tvoc_threshold = 100.0

        manual_override_val = settings_map.get("manual_override", "0")
        manual_override = manual_override_val == 1 or manual_override_val in {"1", "true", "True"}

        manual_alert_val = settings_map.get("manual_alert_enabled", "0")
        manual_alert_enabled = manual_alert_val == 1 or manual_alert_val in {"1", "true", "True"}

        return {
            "tvoc_threshold": tvoc_threshold,
            "manual_override": manual_override,
            "manual_alert_enabled": manual_alert_enabled,
        }

    def update_tvoc_threshold(self, value: float) -> float:
        sql = """
            INSERT INTO settings (setting_key, setting_value)
            VALUES ('tvoc_threshold', %s)
            ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (str(value),))
        return value

    def set_manual_override(self, enabled: bool) -> tuple[bool, bool]:
        override_val = "1" if enabled else "0"
        alert_val = "1" if enabled else "0"

        sql = """
            INSERT INTO settings (setting_key, setting_value)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(sql, ("manual_override", override_val))
            cursor.execute(sql, ("manual_alert_enabled", alert_val))

        return enabled, enabled
