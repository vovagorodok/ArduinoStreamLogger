#pragma once
#include <ostream>

enum class LoggingLevel
{
    Trace = 0,
    Debug = 1,
    Info = 2,
    Warning = 3,
    Error = 4,
    None = 5
};
extern const LoggingLevel loggingLevel;

std::ostream& trace();
std::ostream& debug();
std::ostream& info();
std::ostream& warning();
std::ostream& error();

#define SET_LOGGING_LEVEL(level) const LoggingLevel loggingLevel = level;
#define LOG_TRACE trace()
#define LOG_DEBUG debug()
#define LOG_INFO info()
#define LOG_WARNING warning()
#define LOG_ERROR error()