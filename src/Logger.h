#pragma once

#include "LogLevel.h"
#include "LogEntry.h"

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
