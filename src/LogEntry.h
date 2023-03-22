#pragma once

#include "LogLevel.h"
#include "LogUtils.h"
#include <Arduino.h>

template <LogLevel level>
struct LogEntry {
    LogEntry(const LogEntry&) = delete;

    LogEntry() {
        #ifdef LOGGER_WITH_MUTEX
        loggerMutex.lock();
        #endif

        #ifndef LOG_LEVEL_DISABLED
        #ifdef LOG_FORMAT_WITH_PREFIX
        logPrefix<level>();
        #endif
        #endif
    }

    ~LogEntry() {
        #ifdef LOGGER_WITH_MUTEX
        loggerMutex.unlock();
        #endif
    }

    template <class T>
    inline LogEntry& operator<<(const T& value) {
        #ifndef LOG_LEVEL_DISABLED
        std::cout << value;
        #endif
        return *this;
    }

    inline LogEntry& operator<<(const String& value) {
        #ifndef LOG_LEVEL_DISABLED
        std::cout << value.c_str();
        #endif
        return *this;
    }
};

template <LogLevel level>
struct LogEntryWithEndl : LogEntry<level> {
    LogEntryWithEndl(const LogEntryWithEndl&) = delete;
    LogEntryWithEndl(): LogEntry<level>() {}

    ~LogEntryWithEndl() {
        #ifndef LOG_LEVEL_DISABLED
        std::cout << std::endl;
        #endif
    }
};

enum class NoLogEntry {};

template <typename T>
[[maybe_unused]] constexpr NoLogEntry operator<<(const NoLogEntry noLogEntry, T value) {
    return noLogEntry;
}
