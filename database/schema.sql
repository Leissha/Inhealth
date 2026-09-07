CREATE DATABASE IF NOT EXISTS temperature_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE temperature_db;

CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temp_analog_c DECIMAL(5, 2) NULL,
    temp_digital_c DECIMAL(5, 2) NULL,
    humidity DECIMAL(5, 2) NULL,
    aqi TINYINT UNSIGNED NULL,
    tvoc INT UNSIGNED NULL,
    eco2 INT UNSIGNED NULL,
    pm1 DECIMAL(7, 2) NULL,
    pm25 DECIMAL(7, 2) NULL,
    pm10 DECIMAL(7, 2) NULL,
    PRIMARY KEY (id),
    INDEX idx_sensor_readings_recorded_at (recorded_at),
    CONSTRAINT chk_aqi_range CHECK (aqi IS NULL OR aqi BETWEEN 1 AND 5),
    CONSTRAINT chk_humidity_range CHECK (
        humidity IS NULL OR humidity BETWEEN 0 AND 100
    )
);

CREATE TABLE IF NOT EXISTS settings (
    setting_key VARCHAR(50) NOT NULL,
    setting_value VARCHAR(255) NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (setting_key)
);

CREATE TABLE IF NOT EXISTS alert_events (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    state TINYINT(1) NOT NULL,
    trigger_mode VARCHAR(20) NOT NULL,
    tvoc_value INT UNSIGNED NULL,
    tvoc_threshold DECIMAL(10, 2) NULL,
    PRIMARY KEY (id),
    INDEX idx_alert_events_occurred_at (occurred_at)
);

INSERT INTO settings (setting_key, setting_value)
VALUES
    ('tvoc_threshold', '100'),
    ('manual_override', '0'),
    ('manual_alert_enabled', '0')
ON DUPLICATE KEY UPDATE setting_key = VALUES(setting_key);
