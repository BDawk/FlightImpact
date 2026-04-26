/*
 * FlightImpact dev kit — Uno R3 firmware
 *
 * Roles (Phase 1):
 *   - LED strobe driver on D9 (PWM)
 *   - Hardware trigger pulse output on D8 (digital, ~5us)
 *   - Heartbeat LED on D13
 *   - Listens on serial (115200 baud) for commands from the Pi
 *
 * Future roles (Phase 2+):
 *   - ADC sampler streaming HB100 IF samples to Pi at 20 kHz
 *
 * Serial protocol (text-based, line-terminated):
 *   "PING\n"            -> "PONG\n"
 *   "TRIG\n"            -> fire trigger pulse, reply "OK\n"
 *   "STROBE <ms>\n"     -> turn on strobe for <ms> milliseconds
 *   "STROBE OFF\n"      -> strobe off
 *   "ID\n"              -> reply "FLIGHTIMPACT-DEVKIT v0.1\n"
 *
 * Frame format (when streaming samples in Phase 2):
 *   0xAA 0x55 [n_lo n_hi] [n samples * 2 bytes int16 LE]
 */

#include <Arduino.h>

constexpr uint8_t PIN_TRIGGER = 8;
constexpr uint8_t PIN_STROBE  = 9;
constexpr uint8_t PIN_HEARTBEAT = 13;
constexpr uint16_t TRIGGER_PULSE_US = 100;

uint32_t lastHeartbeat = 0;
uint32_t strobeUntil = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_TRIGGER, OUTPUT);
  pinMode(PIN_STROBE, OUTPUT);
  pinMode(PIN_HEARTBEAT, OUTPUT);
  digitalWrite(PIN_TRIGGER, LOW);
  analogWrite(PIN_STROBE, 0);

  // Quick self-test blink so we know it booted
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_HEARTBEAT, HIGH);
    delay(80);
    digitalWrite(PIN_HEARTBEAT, LOW);
    delay(80);
  }
}

void firePulse() {
  digitalWrite(PIN_TRIGGER, HIGH);
  delayMicroseconds(TRIGGER_PULSE_US);
  digitalWrite(PIN_TRIGGER, LOW);
}

void handleCommand(const String& cmd) {
  if (cmd == "PING") {
    Serial.println("PONG");
  } else if (cmd == "TRIG") {
    firePulse();
    Serial.println("OK");
  } else if (cmd.startsWith("STROBE ")) {
    String arg = cmd.substring(7);
    if (arg == "OFF") {
      analogWrite(PIN_STROBE, 0);
      strobeUntil = 0;
    } else {
      uint32_t ms = arg.toInt();
      if (ms > 0 && ms < 5000) {
        analogWrite(PIN_STROBE, 255);
        strobeUntil = millis() + ms;
      }
    }
    Serial.println("OK");
  } else if (cmd == "ID") {
    Serial.println("FLIGHTIMPACT-DEVKIT v0.1");
  } else {
    Serial.print("ERR Unknown: ");
    Serial.println(cmd);
  }
}

String inputBuffer;

void loop() {
  // Heartbeat LED — 1 Hz blink
  uint32_t now = millis();
  if (now - lastHeartbeat > 500) {
    digitalWrite(PIN_HEARTBEAT, !digitalRead(PIN_HEARTBEAT));
    lastHeartbeat = now;
  }

  // Strobe auto-off
  if (strobeUntil > 0 && now >= strobeUntil) {
    analogWrite(PIN_STROBE, 0);
    strobeUntil = 0;
  }

  // Serial command parsing
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (inputBuffer.length() > 0) {
        handleCommand(inputBuffer);
        inputBuffer = "";
      }
    } else {
      inputBuffer += c;
      if (inputBuffer.length() > 64) {
        inputBuffer = "";  // overflow protection
      }
    }
  }
}
