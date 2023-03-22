#pragma once

#include "LogLevel.h"
#include <Arduino.h>
#ifndef LOG_LEVEL_DISABLED
#include <iostream>
#endif

struct LogNoEndlEntry {
    LogNoEndlEntry(const LogNoEndlEntry&) = delete;
    LogNoEndlEntry(LogLevel level);
    ~LogNoEndlEntry();

    template <class T>
    inline LogNoEndlEntry& operator<<(const T& value) {
        #ifndef LOG_LEVEL_DISABLED
        std::cout << value;
        #endif
        return *this;
    }
    inline LogNoEndlEntry& operator<<(const String& value) {
        #ifndef LOG_LEVEL_DISABLED
        std::cout << value.c_str();
        #endif
        return *this;
    }
};

struct LogEntry : LogNoEndlEntry {
    LogEntry(const LogEntry&) = delete;
    LogEntry(LogLevel level);
    ~LogEntry();
};

enum class NoLogEntry {};

template <typename T>
[[maybe_unused]] constexpr NoLogEntry operator<<(const NoLogEntry noLogEntry, T value) {
    return noLogEntry;
}
