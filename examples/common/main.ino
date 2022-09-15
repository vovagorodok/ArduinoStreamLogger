#include <Arduino.h>
#include <Logger.h>

void setup() {
  Serial.begin(115200);
  while (!Serial);
}

void loop() {
  delay(1000);
  LOG_DEBUG << "debug";
  LOG_INFO << "info";
  LOG_WARNING << "warning";
  LOG_ERROR << "error";
}