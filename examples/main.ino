#include <Arduino.h>
#include <Logger.h>

#if !defined(LOG_LEVEL_DISABLED) && !defined(ESP8266) && !defined(ESP32)
#define LOG_INIT_STREAM
#endif

#ifdef LOG_INIT_STREAM
extern "C" {
int _write(int fd, char *ptr, int len) {
  (void) fd;
  return Serial.write(ptr, len);
}
}
#endif

void setup() {
  #ifndef LOG_LEVEL_DISABLED
  Serial.begin(115200);
  while (!Serial);
  #endif
}

void loop() {
  delay(1000);
  LOG_TRACE << "trace";
  LOG_DEBUG << "debug";
  LOG_INFO << "info";
  LOG_WARNING << "warning";
  LOG_ERROR << "error";
}