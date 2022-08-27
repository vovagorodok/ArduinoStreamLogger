#include <Arduino.h>
#include <Logger.h>

const LoggingLevel loggingLevel = LoggingLevel::Info;

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