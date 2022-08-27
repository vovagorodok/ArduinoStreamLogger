#include <Arduino.h>
#include <Logger.h>

const LoggingLevel loggingLevel = LoggingLevel::Info;

void setup() {
  Serial.begin(115200);
  while (!Serial);
}

void loop() {
  delay(1000);
  debug() << "debug" << std::endl;
  info() << "info" << std::endl;
  error() << "error" << std::endl;
}