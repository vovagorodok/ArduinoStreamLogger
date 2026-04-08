#pragma once
#include "LogLevel.h"
#include "LogFormat.h"
#include "LogArduino.h"

#if defined(LOG_LEVEL_TRACE) || defined(LOG_LVL_TRACE)
    #define PRINTF_LEVEL_TRACE
    #define PRINTF_LEVEL_DEBUG
    #define PRINTF_LEVEL_INFO
    #define PRINTF_LEVEL_WARNING
    #define PRINTF_LEVEL_ERROR
#elif defined(LOG_LEVEL_DEBUG) || defined(LOG_LVL_DEBUG)
    #define PRINTF_LEVEL_DEBUG
    #define PRINTF_LEVEL_INFO
    #define PRINTF_LEVEL_WARNING
    #define PRINTF_LEVEL_ERROR
#elif defined(LOG_LEVEL_INFO) || defined(LOG_LVL_INFO)
    #define PRINTF_LEVEL_INFO
    #define PRINTF_LEVEL_WARNING
    #define PRINTF_LEVEL_ERROR
#elif defined(LOG_LEVEL_WARNING) || defined(LOG_LVL_WARNING)
    #define PRINTF_LEVEL_WARNING
    #define PRINTF_LEVEL_ERROR
#elif defined(LOG_LEVEL_ERROR) || defined(LOG_LVL_ERROR)
    #define PRINTF_LEVEL_ERROR
#endif

#if defined(ARDUINO_ARCH_ESP32) || defined(ARDUINO_ARCH_ESP8266)
    #define PRINTF_LOG Serial.printf
#else
    #define PRINTF_LOG printf
#endif

#define PRINTF_NOOP do {} while (0)

#ifdef PRINTF_LEVEL_TRACE
    #define PRINTF_TRACE(fmt, ...)       PRINTF_LOG("TRC" LOG_FORMAT_SEPARATOR fmt "\n", ##__VA_ARGS__)
    #define PRINTF_BEGIN_TRACE(fmt, ...) PRINTF_LOG("TRC" LOG_FORMAT_SEPARATOR fmt, ##__VA_ARGS__)
    #define PRINTF_ADD_TRACE(fmt, ...)   PRINTF_LOG(fmt, ##__VA_ARGS__)
    #define PRINTF_END_TRACE(fmt, ...)   PRINTF_LOG(fmt "\n", ##__VA_ARGS__)
#else
    #define PRINTF_TRACE(fmt, ...)       PRINTF_NOOP
    #define PRINTF_BEGIN_TRACE(fmt, ...) PRINTF_NOOP
    #define PRINTF_ADD_TRACE(fmt, ...)   PRINTF_NOOP
    #define PRINTF_END_TRACE(fmt, ...)   PRINTF_NOOP
#endif

#ifdef PRINTF_LEVEL_DEBUG
    #define PRINTF_DEBUG(fmt, ...)       PRINTF_LOG("DBG" LOG_FORMAT_SEPARATOR fmt "\n", ##__VA_ARGS__)
    #define PRINTF_BEGIN_DEBUG(fmt, ...) PRINTF_LOG("DBG" LOG_FORMAT_SEPARATOR fmt, ##__VA_ARGS__)
    #define PRINTF_ADD_DEBUG(fmt, ...)   PRINTF_LOG(fmt, ##__VA_ARGS__)
    #define PRINTF_END_DEBUG(fmt, ...)   PRINTF_LOG(fmt "\n", ##__VA_ARGS__)
#else
    #define PRINTF_DEBUG(fmt, ...)       PRINTF_NOOP
    #define PRINTF_BEGIN_DEBUG(fmt, ...) PRINTF_NOOP
    #define PRINTF_ADD_DEBUG(fmt, ...)   PRINTF_NOOP
    #define PRINTF_END_DEBUG(fmt, ...)   PRINTF_NOOP
#endif

#ifdef PRINTF_LEVEL_INFO
    #define PRINTF_INFO(fmt, ...)       PRINTF_LOG("INF" LOG_FORMAT_SEPARATOR fmt "\n", ##__VA_ARGS__)
    #define PRINTF_BEGIN_INFO(fmt, ...) PRINTF_LOG("INF" LOG_FORMAT_SEPARATOR fmt, ##__VA_ARGS__)
    #define PRINTF_ADD_INFO(fmt, ...)   PRINTF_LOG(fmt, ##__VA_ARGS__)
    #define PRINTF_END_INFO(fmt, ...)   PRINTF_LOG(fmt "\n", ##__VA_ARGS__)
#else
    #define PRINTF_INFO(fmt, ...)       PRINTF_NOOP
    #define PRINTF_BEGIN_INFO(fmt, ...) PRINTF_NOOP
    #define PRINTF_ADD_INFO(fmt, ...)   PRINTF_NOOP
    #define PRINTF_END_INFO(fmt, ...)   PRINTF_NOOP
#endif

#ifdef PRINTF_LEVEL_WARNING
    #define PRINTF_WARNING(fmt, ...)       PRINTF_LOG("WRN" LOG_FORMAT_SEPARATOR fmt "\n", ##__VA_ARGS__)
    #define PRINTF_BEGIN_WARNING(fmt, ...) PRINTF_LOG("WRN" LOG_FORMAT_SEPARATOR fmt, ##__VA_ARGS__)
    #define PRINTF_ADD_WARNING(fmt, ...)   PRINTF_LOG(fmt, ##__VA_ARGS__)
    #define PRINTF_END_WARNING(fmt, ...)   PRINTF_LOG(fmt "\n", ##__VA_ARGS__)  
#else
    #define PRINTF_WARNING(fmt, ...)       PRINTF_NOOP
    #define PRINTF_BEGIN_WARNING(fmt, ...) PRINTF_NOOP
    #define PRINTF_ADD_WARNING(fmt, ...)   PRINTF_NOOP
    #define PRINTF_END_WARNING(fmt, ...)   PRINTF_NOOP
#endif

#ifdef PRINTF_LEVEL_ERROR
    #define PRINTF_ERROR(fmt, ...)       PRINTF_LOG("ERR" LOG_FORMAT_SEPARATOR fmt "\n", ##__VA_ARGS__)
    #define PRINTF_BEGIN_ERROR(fmt, ...) PRINTF_LOG("ERR" LOG_FORMAT_SEPARATOR fmt, ##__VA_ARGS__)
    #define PRINTF_ADD_ERROR(fmt, ...)   PRINTF_LOG(fmt, ##__VA_ARGS__)
    #define PRINTF_END_ERROR(fmt, ...)   PRINTF_LOG(fmt "\n", ##__VA_ARGS__)
#else
    #define PRINTF_ERROR(fmt, ...)       PRINTF_NOOP
    #define PRINTF_BEGIN_ERROR(fmt, ...) PRINTF_NOOP
    #define PRINTF_ADD_ERROR(fmt, ...)   PRINTF_NOOP
    #define PRINTF_END_ERROR(fmt, ...)   PRINTF_NOOP
#endif
