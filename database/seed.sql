USE temperature_db;

-- Re-running this file replaces only the development seed readings.
DELETE FROM sensor_readings;

DELIMITER //

DROP PROCEDURE IF EXISTS seed_sensor_readings//
CREATE PROCEDURE seed_sensor_readings()
BEGIN
    DECLARE sample_number INT DEFAULT 0;
    DECLARE sample_tvoc INT;

    WHILE sample_number < 96 DO
        -- Four realistic elevated periods demonstrate the configurable alert rule.
        SET sample_tvoc = CASE
            WHEN sample_number IN (18, 19, 52, 53, 54, 79) THEN
                112 + MOD(sample_number * 7, 34)
            ELSE
                42 + MOD(sample_number * 11, 48)
        END;

        INSERT INTO sensor_readings (
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
        ) VALUES (
            DATE_SUB(
                DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00'),
                INTERVAL (95 - sample_number) * 15 MINUTE
            ),
            ROUND(23.20 + SIN(sample_number / 8.0) * 1.10, 2),
            ROUND(23.60 + SIN((sample_number + 2) / 8.0) * 1.00, 2),
            ROUND(53.00 + SIN(sample_number / 10.0) * 4.50, 2),
            CASE WHEN sample_tvoc >= 125 THEN 3
                 WHEN sample_tvoc >= 90 THEN 2
                 ELSE 1 END,
            sample_tvoc,
            445 + MOD(sample_number * 13, 175),
            ROUND(3.20 + MOD(sample_number * 5, 18) / 10.0, 2),
            ROUND(5.80 + MOD(sample_number * 7, 32) / 10.0, 2),
            ROUND(8.40 + MOD(sample_number * 9, 45) / 10.0, 2)
        );

        SET sample_number = sample_number + 1;
    END WHILE;
END//

DELIMITER ;

CALL seed_sensor_readings();
DROP PROCEDURE seed_sensor_readings;

