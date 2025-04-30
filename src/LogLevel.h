#pragma once

enum class LogLevel {
    trace,
    debug,
    info,
    warning,
    error,
    disabled
};

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
#elif defined LOG_LVL_TRACE
#define LOG_LEVEL LogLevel::trace
#elif defined LOG_LVL_DEBUG
#define LOG_LEVEL LogLevel::debug
#elif defined LOG_LVL_INFO
#define LOG_LEVEL LogLevel::info
#elif defined LOG_LVL_WARNING
#define LOG_LEVEL LogLevel::warning
#elif defined LOG_LVL_ERROR
#define LOG_LEVEL LogLevel::error
#elif defined LOG_LVL_DISABLED
#define LOG_LEVEL LogLevel::disabled
#elif !defined LOG_LEVEL
#define LOG_LEVEL_DISABLED
#define LOG_LEVEL LogLevel::disabled
#endif
