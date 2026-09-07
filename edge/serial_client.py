from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None  # type: ignore


class SerialClient:
    def __init__(self, port: str = "", baud_rate: int = 9600, timeout: float = 1.0) -> None:
        self.configured_port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.connection: Any = None

    def find_port(self) -> str | None:
        if self.configured_port and self.configured_port.strip():
            return self.configured_port.strip()

        if serial is None:
            return None

        # Auto-detect available COM or ttyACM / ttyUSB ports
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            device = p.device
            if "ttyACM" in device or "ttyUSB" in device or device.startswith("COM"):
                logger.info("Auto-detected serial device: %s (%s)", device, p.description)
                return device

        return None

    def connect(self) -> bool:
        if serial is None:
            logger.warning("pyserial is not installed. Serial communication disabled.")
            return False

        if self.connection and self.connection.is_open:
            return True

        port = self.find_port()
        if not port:
            logger.warning("No serial port configured or detected.")
            return False

        try:
            self.connection = serial.Serial(port, self.baud_rate, timeout=self.timeout)
            logger.info("Connected to serial device on %s @ %d baud", port, self.baud_rate)
            return True
        except Exception as err:
            logger.error("Failed to connect to serial port %s: %s", port, err)
            self.connection = None
            return False

    def close(self) -> None:
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception:
                pass
        self.connection = None

    def read_line(self) -> str | None:
        if not self.connect() or not self.connection:
            return None

        try:
            raw = self.connection.readline()
            if not raw:
                return None
            return raw.decode("utf-8", errors="replace").strip()
        except Exception as err:
            logger.error("Error reading serial line: %s", err)
            self.close()
            return None

    def set_alert(self, enabled: bool) -> bool:
        if not self.connect() or not self.connection:
            return False

        command = b"ALERT_ON\n" if enabled else b"ALERT_OFF\n"
        try:
            self.connection.write(command)
            self.connection.flush()
            logger.info("Sent serial command: %s", command.strip().decode("ascii"))
            return True
        except Exception as err:
            logger.error("Failed to send serial command: %s", err)
            self.close()
            return False
