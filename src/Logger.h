#pragma once
#include "LogLevel.h"
#include "LogEntry.h"

#define LOG_TRACE   LOG<LogLevel::trace>()
#define LOG_DEBUG   LOG<LogLevel::debug>()
#define LOG_INFO    LOG<LogLevel::info>()
#define LOG_WARNING LOG<LogLevel::warning>()
#define LOG_ERROR   LOG<LogLevel::error>()

#define LOG_COMBINE_TRACE   LOG_COMBINE<LogLevel::trace>()
#define LOG_COMBINE_DEBUG   LOG_COMBINE<LogLevel::debug>()
#define LOG_COMBINE_INFO    LOG_COMBINE<LogLevel::info>()
#define LOG_COMBINE_WARNING LOG_COMBINE<LogLevel::warning>()
#define LOG_COMBINE_ERROR   LOG_COMBINE<LogLevel::error>()

#define LOG_CALL_TRACE(ex)   if constexpr (isLogged(LogLevel::trace))   LOG_TRACE ex
#define LOG_CALL_DEBUG(ex)   if constexpr (isLogged(LogLevel::debug))   LOG_DEBUG ex
#define LOG_CALL_INFO(ex)    if constexpr (isLogged(LogLevel::info))    LOG_INFO ex
#define LOG_CALL_WARNING(ex) if constexpr (isLogged(LogLevel::warning)) LOG_WARNING ex
#define LOG_CALL_ERROR(ex)   if constexpr (isLogged(LogLevel::error))   LOG_ERROR ex

#define LOG_CALL_COMBINE_TRACE(ex)   if constexpr (isLogged(LogLevel::trace))   LOG_COMBINE_TRACE ex
#define LOG_CALL_COMBINE_DEBUG(ex)   if constexpr (isLogged(LogLevel::debug))   LOG_COMBINE_DEBUG ex
#define LOG_CALL_COMBINE_INFO(ex)    if constexpr (isLogged(LogLevel::info))    LOG_COMBINE_INFO ex
#define LOG_CALL_COMBINE_WARNING(ex) if constexpr (isLogged(LogLevel::warning)) LOG_COMBINE_WARNING ex
#define LOG_CALL_COMBINE_ERROR(ex)   if constexpr (isLogged(LogLevel::error))   LOG_COMBINE_ERROR ex

constexpr bool isLogged(LogLevel level) {
    return LOG_LEVEL <= level;
}

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG() {
    if constexpr (isLogged(level)) {
        return LogEntryWithEndl<level>();
    } else {
        return NoLogEntry();
    }
};

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG_COMBINE() {
    if constexpr (isLogged(level)) {
        return LogEntry<level>();
    } else {
        return NoLogEntry();
    }
};
