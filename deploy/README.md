# Inhealth edge VM deployment

The final application runs on the Debian Raspberry Pi VM. Windows is used for
development and as the browser client.

```text
Arduino USB
    -> inhealth-edge
    -> MariaDB
    -> inhealth-backend (FastAPI + Vue)
    -> browser
```

Control requests travel in the other direction:

```text
browser -> FastAPI -> MariaDB settings -> inhealth-edge -> Arduino
```

Only `inhealth-edge` opens the Arduino serial device.

## Deployed paths

| Item | VM location |
| --- | --- |
| Project | `/home/admin/inhealth/webapp` |
| Python environment | `/home/admin/inhealth/venv` |
| Runtime configuration | `/home/admin/inhealth/webapp/.env` |
| Backend service | `/etc/systemd/system/inhealth-backend.service` |
| Edge service | `/etc/systemd/system/inhealth-edge.service` |

Keep the `.env` file outside version control and restrict it to the service user.

## Required configuration

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=temperature_db
SERIAL_BAUD_RATE=9600
SERIAL_PORT=/dev/serial/by-id/<Arduino identity>
```

The `/dev/serial/by-id/` path is preferred because `/dev/ttyACM0` can change
after a reconnect. Both names point to the same device when the Arduino is
currently assigned `ttyACM0`.

## Deploy an update

1. Back up the current project and database.
2. Run the Python tests and Vue production build on Windows.
3. Copy `backend`, `edge`, `database`, `frontend/dist`, `deploy` and the Python
   dependency file to the VM.
4. Keep the VM's existing `.env`; do not copy credentials into documentation.
5. Install changed Python dependencies in the VM environment.
6. Restart both services.
7. Verify logs, API routes and the browser interface.

Do not run `database/seed.sql` against the demonstration database. It is only for
creating local development data.

## Service checks

Connect from Windows PowerShell first:

```powershell
ssh -p 2222 admin@127.0.0.1
```

Then run these commands inside the VM:

```sh
sudo systemctl status inhealth-backend inhealth-edge
sudo journalctl -u inhealth-edge -n 40 --no-pager
sudo systemctl restart inhealth-backend inhealth-edge
```

Expected startup evidence includes:

```text
Connected to serial device ... @ 9600 baud
Database insert succeeded; ingestion started
Arduino acknowledgement: ACK=ALERT_OFF
```

## Current serial frame

The PMS7003 is physically integrated. The Arduino frame now includes all particle
fields on every sample:

```text
TEMP_ANALOG_C=..., TEMP_DIGITAL_C=..., HUMIDITY=...,
AQI=..., TVOC=..., ECO2=..., PM1=..., PM25=..., PM10=...
```

If a valid PMS frame has not arrived recently, the firmware sends `NULL` for the
three PM fields. It does not remove the keys. This fixed shape lets the edge reject
truncated or old-format frames.

## Data validation

Validation happens once in `edge/sensor_parser.py`, before insertion:

1. Ignore empty, status and ACK messages.
2. Split the serial frame into labelled tokens.
3. Convert each known value with `parse_value()`.
4. Reject frames missing current required fields.
5. Apply range and contact-loss rules in `normalize_reading()`.
6. Store the normalized reading.

The API repository reads normalized database rows. It does not repeat legacy AQI
or ENS160 correction in SQL. History and statistics still exclude `NULL` values.

## USB troubleshooting

If the VM cannot see the Arduino:

1. Close Arduino Serial Monitor on Windows.
2. Attach the Arduino USB device to the VM in VirtualBox.
3. Confirm it appears with `lsusb`.
4. Check `/dev/serial/by-id/` and `/dev/ttyACM*`.
5. Restart `inhealth-edge`.
6. Follow its log and confirm a new database row.

Do not run a second serial monitor while `inhealth-edge` owns the port.

## Final demonstration checks

- The Python suite reports `35 passed`.
- The Vue production build completes.
- Current sensor rows include non-NULL PM1, PM2.5 and PM10 values.
- Dashboard, Analytics and Controls load from the VM address.
- Test Alert turns on the physical LED and buzzer.
- Stop Alert turns both outputs off.
- Lowering the TVOC threshold triggers the automatic alert.
- Restoring the threshold to 100 ppb and automatic mode leaves safe settings.

An HTTP success response or Arduino ACK proves communication. The final video
must also show the physical LED and buzzer to prove actuation.
