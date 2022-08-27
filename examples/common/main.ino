#include <Arduino.h>
#include <Logger.h>

SET_LOGGING_LEVEL(LoggingLevel::Info)

void setup() {
  Serial.begin(115200);
  while (!Serial);
}

void loop() {
  delay(1000);
  LOG_DEBUG << "debug" << std::endl;
  LOG_INFO << "info" << std::endl;
  LOG_ERROR << "error" << std::endl;
}