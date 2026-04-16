#pragma once
#include "LogLevel.h"
#include "LogFormat.h"

#if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
#include <ostream>

template <LogLevel level>
constexpr void logPrefix(std::ostream& os) {
    if constexpr (level == LogLevel::trace)
        os << "TRC" << LOG_FORMAT_SEPARATOR;
    if constexpr (level == LogLevel::debug)
        os << "DBG" << LOG_FORMAT_SEPARATOR;
    if constexpr (level == LogLevel::info)
        os << "INF" << LOG_FORMAT_SEPARATOR;
    if constexpr (level == LogLevel::warning)
        os << "WRN" << LOG_FORMAT_SEPARATOR;
    if constexpr (level == LogLevel::error)
        os << "ERR" << LOG_FORMAT_SEPARATOR;
}

#endif
