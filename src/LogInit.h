#pragma once
#include <Arduino.h>

#if !defined(ESP8266) && !defined(ESP32)
extern "C" {
int _write(int fd, char *ptr, int len) {
  (void) fd;
  return Serial.write(ptr, len);
}
}
#endif