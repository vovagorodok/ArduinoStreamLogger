#include "Logger.h"

#ifndef LOG_LEVEL_DISABLED
#if defined(ESP32)
#define LOGGER_WITH_MUTEX

#include <mutex>
namespace
{
static std::mutex loggerMutex{};
}
#endif
#endif

LogNoEndlEntry::LogNoEndlEntry(LogLevel level)
{
    #ifndef LOG_LEVEL_DISABLED

    #ifdef LOGGER_WITH_MUTEX
    loggerMutex.lock();
    #endif

    #ifdef LOG_FORMAT_WITH_PREFIX
    switch (level) {
        case LogLevel::trace:
            std::cout << "TRC: ";
            break;
        case LogLevel::debug:
            std::cout << "DBG: ";
            break;
        case LogLevel::info:
            std::cout << "INF: ";
            break;
        case LogLevel::warning:
            std::cout << "WRN: ";
            break;
        case LogLevel::error:
            std::cout << "ERR: ";
            break;
        default:
            break;
    }
    #endif

    #endif
}

LogNoEndlEntry::~LogNoEndlEntry()
{
    #ifdef LOGGER_WITH_MUTEX
    loggerMutex.unlock();
    #endif
}

LogEntry::LogEntry(LogLevel level) :
    LogNoEndlEntry(level)
{}

LogEntry::~LogEntry()
{
    #ifndef LOG_LEVEL_DISABLED
    std::cout << std::endl;
    #endif
}