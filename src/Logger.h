#pragma once

#if defined LOG_LEVEL_TRACE
#define LOG_LEVEL LogLevel::trace
#elif defined LOG_LEVEL_DEBUG
#define LOG_LEVEL LogLevel::debug
#elif defined LOG_LEVEL_INFO
#define LOG_LEVEL LogLevel::info
#elif defined LOG_LEVEL_WARNING
#define LOG_LEVEL LogLevel::warning
#elif defined LOG_LEVEL_ERROR
#define LOG_LEVEL LogLevel::error
#elif defined LOG_LEVEL_DISABLED
#define LOG_LEVEL LogLevel::disabled
#elif !defined LOG_LEVEL
#define LOG_LEVEL_DISABLED
#define LOG_LEVEL LogLevel::disabled
#endif

#include <Arduino.h>
#ifndef LOG_LEVEL_DISABLED
#include <iostream>
#endif

#define LOG_TRACE   LOG<LogLevel::trace>()
#define LOG_DEBUG   LOG<LogLevel::debug>()
#define LOG_INFO    LOG<LogLevel::info>()
#define LOG_WARNING LOG<LogLevel::warning>()
#define LOG_ERROR   LOG<LogLevel::error>()

#define LOG_NO_ENDL_TRACE   LOG_NO_ENDL<LogLevel::trace>()
#define LOG_NO_ENDL_DEBUG   LOG_NO_ENDL<LogLevel::debug>()
#define LOG_NO_ENDL_INFO    LOG_NO_ENDL<LogLevel::info>()
#define LOG_NO_ENDL_WARNING LOG_NO_ENDL<LogLevel::warning>()
#define LOG_NO_ENDL_ERROR   LOG_NO_ENDL<LogLevel::error>()

#define LOG_CALL_IF_TRACE(ex)   if constexpr (isLogged(LogLevel::trace))   ex
#define LOG_CALL_IF_DEBUG(ex)   if constexpr (isLogged(LogLevel::debug))   ex
#define LOG_CALL_IF_INFO(ex)    if constexpr (isLogged(LogLevel::info))    ex
#define LOG_CALL_IF_WARNING(ex) if constexpr (isLogged(LogLevel::warning)) ex
#define LOG_CALL_IF_ERROR(ex)   if constexpr (isLogged(LogLevel::error))   ex

enum class LogLevel {
    trace,
    debug,
    info,
    warning,
    error,
    disabled
};

enum class NoLogEntry {};

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

constexpr bool isLogged(LogLevel level) {
    return LOG_LEVEL <= level;
}

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG() {
    if constexpr (isLogged(level)) {
        return LogEntry(level);
    } else {
        return NoLogEntry();
    }
};

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG_NO_ENDL() {
    if constexpr (isLogged(level)) {
        return LogNoEndlEntry(level);
    } else {
        return NoLogEntry();
    }
};

template <typename T>
[[maybe_unused]] constexpr NoLogEntry operator<<(const NoLogEntry noLogEntry, T value) {
    return noLogEntry;
}