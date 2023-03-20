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

LogNoEndlEntry::LogNoEndlEntry()
{
    #ifdef LOGGER_WITH_MUTEX
    loggerMutex.lock();
    #endif
}

LogNoEndlEntry::~LogNoEndlEntry()
{
    #ifdef LOGGER_WITH_MUTEX
    loggerMutex.unlock();
    #endif
}

LogEntry::LogEntry() :
    LogNoEndlEntry()
{}

LogEntry::~LogEntry()
{
    #ifndef LOG_LEVEL_DISABLED
    std::cout << std::endl;
    #endif
}