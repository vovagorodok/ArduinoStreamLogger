#pragma once
#include "LogLevel.h"

#if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)

#ifdef ARDUINO_ARCH_ESP32
#include <mutex>
#define LOGGER_WITH_MUTEX

extern std::recursive_mutex loggerMutex;
#endif

#endif
