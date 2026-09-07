// Air Quality Sensor (ENS160 + AHT21): https://ae-pic-a1.aliexpress-media.com/kf/S6fee21f91cbd453681977ef128d29183G.pdf?spm=a2g0o.detail.0.0.2caacSajcSajRB&file=S6fee21f91cbd453681977ef128d29183G.pdf
  // Share the Uno hardware I2C bus: SDA -> A4, SCL -> A5

// Dust Sensor (PMS7003 or D7 UART): https://ae-pic-a1.aliexpress-media.com/kf/Saf043228643243cabd6f77902396632bi.pdf?spm=a2g0o.detail.0.0.78f9F0prF0prwu&file=Saf043228643243cabd6f77902396632bi.pdf 
  // D10 (SoftwareSerial RX) <- PM sensor TXD
  // D11 (SoftwareSerial TX) is unused because the Arduino does not currently send commands to the PM sensor.

#include <Wire.h>
#include <DFRobot_ENS160.h>
#include <PTSolns_AHTx.h>
#include <SoftwareSerial.h>

// -------------------- Pin mapping --------------------
// Sensors
// LM35 analog temperature sensor
const int LM35_ANALOG_TEMP = A0;

// ENS160 + AHT21 share the Uno hardware I2C bus:
// SDA -> A4, SCL -> A5
DFRobot_ENS160_I2C ens160(&Wire, 0x53); // I²C address
PTSolns_AHTx aht;

// PMS7003 / D7 UART:
// D10 (RX) <- sensor TXD
// D11 (TX) is unused; Arduino does not send PM commands
const int PM_RX_PIN = 10;
const int PM_TX_PIN = 11;
SoftwareSerial pmSerial(PM_RX_PIN, PM_TX_PIN);
const int PM_FRAME_LEN = 32;
byte pmFrame[PM_FRAME_LEN];

uint16_t pm1 = 0, pm25 = 0, pm10 = 0;
bool pmAvailable = false;
unsigned long lastPmReadingTime = 0;
const unsigned long PM_STALE_TIMEOUT = 10000; // 10 sec

// Actuators
const int RED_LED = 2;
const int BUZZER = 3;

// Timing
const unsigned long SAMPLE_INTERVAL = 2000; // 2 sec
unsigned long lastSampleTime = 0;

// Resilient system
bool ahtAvailable = false;
bool ensAvailable = false;

const unsigned long I2C_RETRY_INTERVAL = 5000;
unsigned long lastI2CRetryTime = 0;

// ==================================================
// Setup
// ==================================================
void setup() {
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  digitalWrite(RED_LED, LOW);
  noTone(BUZZER);

  // Arduino <-> Raspberry Pi / VM
  Serial.begin(9600);
  // D7 PM sensor
  pmSerial.begin(9600);
  // I2C sensors
  Wire.begin();

  // Initialise I2C sensors and ensure that they respond
  ahtAvailable = aht.begin();

  if (!ahtAvailable) {
    Serial.println("AHT21 unavailable");
  }

  ensAvailable = (ens160.begin() == NO_ERR);

  if (!ensAvailable) {
    Serial.println("ENS160 unavailable");
  }
  else {
    ens160.setPWRMode(ENS160_STANDARD_MODE);
  }

  Serial.println("Sensors initialised");
}


// ==================================================
// Loop
// ==================================================
void loop() {
  processSerialCommand();
  readPmSensor();
  retryI2CSensors();

  unsigned long currentTime = millis();

  // Expire old PM readings
  if (pmAvailable && currentTime - lastPmReadingTime > PM_STALE_TIMEOUT) {
    pmAvailable = false;
  }

  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime = currentTime;
    readAndSendSensorData();
  }
}

// ==================================================
// Main sensor output
// ==================================================
void readAndSendSensorData() {
  // ---------------- LM35 ----------------
  int rawValue = analogRead(LM35_ANALOG_TEMP);
  float voltageMv = rawValue * (5000.0 / 1024.0);
  float tempAnalogC = voltageMv / 10.0;

  // ---------------- AHT21 ----------------
  float tempDigitalC = 0.0;
  float humidity = 0.0;
  bool ahtReadOk = false;

  if (ahtAvailable) {
    AHTxStatus ahtStatus =
        aht.readTemperatureHumidity(tempDigitalC, humidity, 120);

    ahtReadOk = (ahtStatus == AHTX_OK);

    if (!ahtReadOk) {
      ahtAvailable = false;
      Serial.println("AHT21 connection lost");
    }
  }

  // ---------------- ENS160 ----------------
  uint8_t aqi = 0;
  uint16_t tvoc = 0;
  uint16_t eco2 = 0;

  if (ensAvailable) {
    aqi = ens160.getAQI();
    tvoc = ens160.getTVOC();
    eco2 = ens160.getECO2();

    // Known contact-loss pattern for this prototype
    if (aqi == 0 && tvoc == 0 && eco2 == 0) {
      ensAvailable = false;
      Serial.println("ENS160 connection lost");
    }
  }

  // ---------------- Serial output ----------------
  Serial.print(F("TEMP_ANALOG_C="));
  Serial.print(tempAnalogC, 2);

  // AHT21
  if (ahtAvailable && ahtReadOk) {
    Serial.print(F(", TEMP_DIGITAL_C="));
    Serial.print(tempDigitalC, 2);

    Serial.print(F(", HUMIDITY="));
    Serial.print(humidity, 2);
  }
  else {
    Serial.print(F(", TEMP_DIGITAL_C=NULL, HUMIDITY=NULL"));
  }

  // ENS160
  if (ensAvailable) {
    Serial.print(F(", AQI="));
    Serial.print(aqi);

    Serial.print(F(", TVOC="));
    Serial.print(tvoc);

    Serial.print(F(", ECO2="));
    Serial.print(eco2);
  }
  else {
    Serial.print(F(", AQI=NULL, TVOC=NULL, ECO2=NULL"));
  }

  // ---------------- PM ----------------
  if (pmAvailable) {
    Serial.print(F(", PM1="));
    Serial.print(pm1);

    Serial.print(F(", PM25="));
    Serial.print(pm25);

    Serial.print(F(", PM10="));
    Serial.print(pm10);
  }
  else {
    Serial.print(F(", PM1=NULL, PM25=NULL, PM10=NULL"));
  }

  Serial.println();
}                                                                    

// ==================================================
// D7 PM sensor
// ==================================================
void readPmSensor() {
  while (readPmFrame()) {
    // Atmospheric-environment concentrations:
    //  bytes 10–11: PM1.0 , bytes 12–13: PM2.5 , bytes 14–15: PM10
    pm1 = readPmUInt16(10);
    pm25 = readPmUInt16(12);
    pm10 = readPmUInt16(14);

    pmAvailable = true;
    lastPmReadingTime = millis();
  }
}

bool readPmFrame() {
  // Need at least two bytes to search for header 0x42 & 0x4D (https://nodeloop.org/guides/uart-serial-guide/)
  // UART is 9600 baud, 8N1 = ~10 bits/byte
  //  => 9600 bits/s ÷ 10 bits ≈ 960 bytes/s
  //  => 1 byte takes approx 1/960s ≈ 1.04 ms
  //  => 32-byte frame takes approx 32 x 1.04 ≈ 33.3 ms
  // 100-200 ms timeouts provide margin without blocking indefinitely

  while (pmSerial.available() >= 2) {
    // Remove bytes until we find the first frame-header byte (0x42)
    if (pmSerial.peek() != 0x42) {
      pmSerial.read();
      continue;
    }

    // PMS frame header is 0x42 0x4D
    pmFrame[0] = pmSerial.read();
    if (!waitForPmBytes(1, 100)) {
      return false;
    }

    pmFrame[1] = pmSerial.read();
    if (pmFrame[1] != 0x4D) {
      continue;
    }

    // Process the rest of the frame
    if (!waitForPmBytes(PM_FRAME_LEN - 2, 200)){
      return false;
    }
    for (int i = 2; i < PM_FRAME_LEN; i++) {
      pmFrame[i] = pmSerial.read();
    }

    // Expected payload length = 28
    // PM sensor sends 16-bit number as two 8-bit bytes: pmFrame[2] = high byte | pmFrame[3] = low byte
    uint16_t dataLength = ((uint16_t)pmFrame[2] << 8) | pmFrame[3];
    if (dataLength != 28) {
      return false;
    }

    // Verify checksum
    uint16_t calculatedChecksum = 0;
    for (int i = 0; i < 30; i++) {
      calculatedChecksum += pmFrame[i];
    }

    uint16_t receivedChecksum = ((uint16_t)pmFrame[30] << 8) | pmFrame[31];

    if (calculatedChecksum != receivedChecksum){
      return false;
    }

    return true;
  }

  return false;
}

bool waitForPmBytes(int count, unsigned long timeoutMs) {
  unsigned long startTime = millis();

  while (pmSerial.available() < count) {
    if (millis() - startTime >= timeoutMs) 
      return false;
  }
  return true;
}

uint16_t readPmUInt16(int index) {
  return ((uint16_t)pmFrame[index] << 8) | pmFrame[index + 1];
}

// Retry mechanism
void retryI2CSensors() {
  unsigned long currentTime = millis();

  if (currentTime - lastI2CRetryTime < I2C_RETRY_INTERVAL) {
    return;
  }

  lastI2CRetryTime = currentTime;

  if (!ahtAvailable) {
    ahtAvailable = aht.begin();

    if (ahtAvailable) {
      Serial.println("AHT21 reconnected");
    }
  }

  if (!ensAvailable) {
    ensAvailable = (ens160.begin() == NO_ERR);

    if (ensAvailable) {
      ens160.setPWRMode(ENS160_STANDARD_MODE);
      Serial.println("ENS160 reconnected");
    }
  }
}

// ==================================================
// Raspberry Pi -> Arduino commands
// ==================================================
void processSerialCommand() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    command.trim();

    if (command == "ALERT_ON") {
      digitalWrite(RED_LED, HIGH);
      tone(BUZZER, 432);
      Serial.println("ACK=ALERT_ON");
    }
    else if (command == "ALERT_OFF") {
      digitalWrite(RED_LED, LOW);
      noTone(BUZZER);
      Serial.println("ACK=ALERT_OFF");
    }
  }
}