#pragma once
#include <ostream>
#include <iostream>

#if defined LOGLEVEL_TRACE
#define LOGLEVEL LogLevel::trace
#elif defined LOGLEVEL_DEBUG
#define LOGLEVEL LogLevel::debug
#elif defined LOGLEVEL_INFO
#define LOGLEVEL LogLevel::info
#elif defined LOGLEVEL_WARNING
#define LOGLEVEL LogLevel::warning
#elif defined LOGLEVEL_ERROR
#define LOGLEVEL LogLevel::error
#elif defined LOGLEVEL_DISABLED
#define LOGLEVEL LogLevel::disabled
#elif !defined LOGLEVEL
#define LOGLEVEL LogLevel::disabled
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

struct LogEntry {
    LogEntry(const LogEntry&) = delete;
    LogEntry() {}
    ~LogEntry() {
        std::cout << std::endl;
    }

    template <class T>
    LogEntry& operator<<(const T value) {
        std::cout << value;
        return *this;
    }
};

struct LogNoEndlEntry {
    LogNoEndlEntry(const LogNoEndlEntry&) = delete;
    LogNoEndlEntry() {}
    ~LogNoEndlEntry() {}

    template <class T>
    LogNoEndlEntry& operator<<(const T value) {
        std::cout << value;
        return *this;
    }
};

constexpr bool isLogged(LogLevel level) {
    return LOGLEVEL <= level;
}

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG() {
    if constexpr (isLogged(level)) {
        return LogEntry();
    } else {
        return NoLogEntry();
    }
};

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG_NO_ENDL() {
    if constexpr (isLogged(level)) {
        return LogNoEndlEntry();
    } else {
        return NoLogEntry();
    }
};

template <typename T>
[[maybe_unused]] constexpr NoLogEntry operator<<(const NoLogEntry noLogEntry, T value) {
    return noLogEntry;
}