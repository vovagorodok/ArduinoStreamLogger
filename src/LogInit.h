#pragma once
#include "LogLevel.h"
#include <Arduino.h>

#if !defined(LOG_LEVEL_DISABLED) && !defined(ESP8266) && !defined(ESP32)
extern "C" {
int _write(int fd, char *ptr, int len) {
  (void) fd;
  return Serial.write(ptr, len);
}
}
#endif