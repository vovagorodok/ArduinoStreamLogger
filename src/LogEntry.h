#pragma once
#include "LogLevel.h"
#include "LogMutex.h"
#include "LogPrefix.h"
#include "LogArduino.h"
#if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
#include <iostream>
#include <sstream>
#endif

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
};

template <LogLevel level>
struct LogEntryWithStream : LogEntry<level> {
    template <class T>
    inline LogEntryWithStream& operator<<(const T& value) {
        #if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
        std::cout << value;
        #endif
        return *this;
    }

    #ifdef LOG_ARDUINO
    inline LogEntryWithStream& operator<<(const String& value) {
        #if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)
        std::cout << value.c_str();
        #endif
        return *this;
    }
    #endif
};

template <LogLevel level>
struct LogEntryWithPrefix : LogEntryWithStream<level> {
#if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)

    LogEntryWithPrefix(const LogEntryWithPrefix&) = delete;
    LogEntryWithPrefix(): LogEntryWithStream<level>() {
        #ifndef LOG_FORMAT_WITHOUT_PREFIX
        logPrefix<level>(std::cout);
        #endif
    }

#endif
};

template <LogLevel level>
struct LogEntryWithEndl : LogEntryWithStream<level> {
#if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)

    LogEntryWithEndl(const LogEntryWithEndl&) = delete;
    LogEntryWithEndl(): LogEntryWithStream<level>() {}
    ~LogEntryWithEndl() {
        std::cout << std::endl;
    }

#endif
};

template <LogLevel level>
struct LogEntryWithPrefixAndEndl : LogEntryWithStream<level> {
#if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)

    LogEntryWithPrefixAndEndl(const LogEntryWithPrefixAndEndl&) = delete;
    LogEntryWithPrefixAndEndl(): LogEntryWithStream<level>() {
        #ifndef LOG_FORMAT_WITHOUT_PREFIX
        logPrefix<level>(std::cout);
        #endif
    }

    ~LogEntryWithPrefixAndEndl() {
        std::cout << std::endl;
    }

#endif
};

template <LogLevel level>
struct LogEntryWithCache : LogEntry<level> {
#if !defined(LOG_LEVEL_DISABLED) && !defined(LOG_LVL_DISABLED)

    LogEntryWithCache(const LogEntryWithCache&) = delete;
    LogEntryWithCache(std::string& last): LogEntry<level>(), last(last), cache() {
        #ifndef LOG_FORMAT_WITHOUT_PREFIX
        logPrefix<level>(cache);
        #endif
    }

    ~LogEntryWithCache() {
        auto str = cache.str();
        if (str != last) {
            std::cout << str << std::endl;
            last = str;
        }
    }

    template <class T>
    inline LogEntryWithCache& operator<<(const T& value) {
        cache << value;
        return *this;
    }

    #ifdef LOG_ARDUINO
    inline LogEntryWithCache& operator<<(const String& value) {
        cache << value.c_str();
        return *this;
    }
    #endif

private:
    std::string& last;
    std::ostringstream cache;

#endif
};

enum class NoLogEntry {};

template <typename T>
[[maybe_unused]] constexpr NoLogEntry operator<<(const NoLogEntry noLogEntry, T value) {
    return noLogEntry;
}
