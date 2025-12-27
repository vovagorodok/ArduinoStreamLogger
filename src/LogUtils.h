#pragma once
#include "LogLevel.h"

#if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
#include <iostream>

#ifdef ESP32
#include <mutex>
#define LOGGER_WITH_MUTEX

extern std::recursive_mutex loggerMutex;
#endif

#ifndef LOG_FORMAT_SEPARATOR
#define LOG_FORMAT_SEPARATOR ": "
#endif

template <LogLevel level>
constexpr void logPrefix() {
    if constexpr (level == LogLevel::trace)
        std::cout << "TRC" << LOG_FORMAT_SEPARATOR;
    if constexpr (level == LogLevel::debug)
        std::cout << "DBG" << LOG_FORMAT_SEPARATOR;
    if constexpr (level == LogLevel::info)
        std::cout << "INF" << LOG_FORMAT_SEPARATOR;
    if constexpr (level == LogLevel::warning)
        std::cout << "WRN" << LOG_FORMAT_SEPARATOR;
    if constexpr (level == LogLevel::error)
        std::cout << "ERR" << LOG_FORMAT_SEPARATOR;
}

#endif
