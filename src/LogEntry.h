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
    }

    ~LogEntry() {
        #ifdef LOGGER_WITH_MUTEX
        loggerMutex.unlock();
        #endif
    }

    template <class T>
    inline LogEntry& operator<<(const T& value) {
        #if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
        std::cout << value;
        #endif
        return *this;
    }

    inline LogEntry& operator<<(const String& value) {
        #if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
        std::cout << value.c_str();
        #endif
        return *this;
    }
};

template <LogLevel level>
struct LogEntryWithPrefix : LogEntry<level> {
    LogEntryWithPrefix(const LogEntryWithPrefix&) = delete;
    LogEntryWithPrefix(): LogEntry<level>() {
        #if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
        #ifndef LOG_FORMAT_WITHOUT_PREFIX
        logPrefix<level>();
        #endif
        #endif
    }
};

template <LogLevel level>
struct LogEntryWithEndl : LogEntry<level> {
    LogEntryWithEndl(const LogEntryWithEndl&) = delete;
    LogEntryWithEndl(): LogEntry<level>() {}
    ~LogEntryWithEndl() {
        #if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
        std::cout << std::endl;
        #endif
    }
};

template <LogLevel level>
struct LogEntryWithPrefixAndEndl : LogEntry<level> {
    LogEntryWithPrefixAndEndl(const LogEntryWithPrefixAndEndl&) = delete;
    LogEntryWithPrefixAndEndl(): LogEntry<level>() {
        #if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
        #ifndef LOG_FORMAT_WITHOUT_PREFIX
        logPrefix<level>();
        #endif
        #endif
    }

    ~LogEntryWithPrefixAndEndl() {
        #if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
        std::cout << std::endl;
        #endif
    }
};

enum class NoLogEntry {};

template <typename T>
[[maybe_unused]] constexpr NoLogEntry operator<<(const NoLogEntry noLogEntry, T value) {
    return noLogEntry;
}
