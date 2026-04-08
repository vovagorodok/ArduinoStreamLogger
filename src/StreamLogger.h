#pragma once
#include "LogLevel.h"
#include "LogEntry.h"

#define LOG_TRACE   LOG<LogLevel::trace>()
#define LOG_DEBUG   LOG<LogLevel::debug>()
#define LOG_INFO    LOG<LogLevel::info>()
#define LOG_WARNING LOG<LogLevel::warning>()
#define LOG_ERROR   LOG<LogLevel::error>()

#define LOG_BEGIN_TRACE   LOG_BEGIN<LogLevel::trace>()
#define LOG_BEGIN_DEBUG   LOG_BEGIN<LogLevel::debug>()
#define LOG_BEGIN_INFO    LOG_BEGIN<LogLevel::info>()
#define LOG_BEGIN_WARNING LOG_BEGIN<LogLevel::warning>()
#define LOG_BEGIN_ERROR   LOG_BEGIN<LogLevel::error>()

#define LOG_ADD_TRACE   LOG_ADD<LogLevel::trace>()
#define LOG_ADD_DEBUG   LOG_ADD<LogLevel::debug>()
#define LOG_ADD_INFO    LOG_ADD<LogLevel::info>()
#define LOG_ADD_WARNING LOG_ADD<LogLevel::warning>()
#define LOG_ADD_ERROR   LOG_ADD<LogLevel::error>()

#define LOG_END_TRACE   LOG_END<LogLevel::trace>()
#define LOG_END_DEBUG   LOG_END<LogLevel::debug>()
#define LOG_END_INFO    LOG_END<LogLevel::info>()
#define LOG_END_WARNING LOG_END<LogLevel::warning>()
#define LOG_END_ERROR   LOG_END<LogLevel::error>()

#define LOG_CALL_TRACE(ex)   if constexpr (isLogged(LogLevel::trace))   LOG_TRACE ex
#define LOG_CALL_DEBUG(ex)   if constexpr (isLogged(LogLevel::debug))   LOG_DEBUG ex
#define LOG_CALL_INFO(ex)    if constexpr (isLogged(LogLevel::info))    LOG_INFO ex
#define LOG_CALL_WARNING(ex) if constexpr (isLogged(LogLevel::warning)) LOG_WARNING ex
#define LOG_CALL_ERROR(ex)   if constexpr (isLogged(LogLevel::error))   LOG_ERROR ex

#define LOG_CALL_BEGIN_TRACE(ex)   if constexpr (isLogged(LogLevel::trace))   LOG_BEGIN_TRACE ex
#define LOG_CALL_BEGIN_DEBUG(ex)   if constexpr (isLogged(LogLevel::debug))   LOG_BEGIN_DEBUG ex
#define LOG_CALL_BEGIN_INFO(ex)    if constexpr (isLogged(LogLevel::info))    LOG_BEGIN_INFO ex
#define LOG_CALL_BEGIN_WARNING(ex) if constexpr (isLogged(LogLevel::warning)) LOG_BEGIN_WARNING ex
#define LOG_CALL_BEGIN_ERROR(ex)   if constexpr (isLogged(LogLevel::error))   LOG_BEGIN_ERROR ex

#define LOG_CALL_ADD_TRACE(ex)   if constexpr (isLogged(LogLevel::trace))   LOG_ADD_TRACE ex
#define LOG_CALL_ADD_DEBUG(ex)   if constexpr (isLogged(LogLevel::debug))   LOG_ADD_DEBUG ex
#define LOG_CALL_ADD_INFO(ex)    if constexpr (isLogged(LogLevel::info))    LOG_ADD_INFO ex
#define LOG_CALL_ADD_WARNING(ex) if constexpr (isLogged(LogLevel::warning)) LOG_ADD_WARNING ex
#define LOG_CALL_ADD_ERROR(ex)   if constexpr (isLogged(LogLevel::error))   LOG_ADD_ERROR ex

#define LOG_CALL_END_TRACE(ex)   if constexpr (isLogged(LogLevel::trace))   LOG_END_TRACE ex
#define LOG_CALL_END_DEBUG(ex)   if constexpr (isLogged(LogLevel::debug))   LOG_END_DEBUG ex
#define LOG_CALL_END_INFO(ex)    if constexpr (isLogged(LogLevel::info))    LOG_END_INFO ex
#define LOG_CALL_END_WARNING(ex) if constexpr (isLogged(LogLevel::warning)) LOG_END_WARNING ex
#define LOG_CALL_END_ERROR(ex)   if constexpr (isLogged(LogLevel::error))   LOG_END_ERROR ex

constexpr bool isLogged(LogLevel level) {
    return LOG_LEVEL <= level;
}

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG() {
    if constexpr (isLogged(level)) {
        return LogEntryWithPrefixAndEndl<level>();
    } else {
        return NoLogEntry();
    }
};

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG_BEGIN() {
    if constexpr (isLogged(level)) {
        return LogEntryWithPrefix<level>();
    } else {
        return NoLogEntry();
    }
};

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG_ADD() {
    if constexpr (isLogged(level)) {
        return LogEntry<level>();
    } else {
        return NoLogEntry();
    }
};

template <LogLevel level>
constexpr __attribute__((always_inline)) inline auto LOG_END() {
    if constexpr (isLogged(level)) {
        return LogEntryWithEndl<level>();
    } else {
        return NoLogEntry();
    }
};
