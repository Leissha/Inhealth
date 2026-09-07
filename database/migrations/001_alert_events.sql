USE temperature_db;

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
