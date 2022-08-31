#pragma once
#include <ostream>

enum class LoggingLevel
{
    Debug = 0,
    Info = 1,
    Warning = 2,
    Error = 3,
    None = 4
};
extern const LoggingLevel loggingLevel;

std::ostream& debug();
std::ostream& info();
std::ostream& warning();
std::ostream& error();

#define SET_LOGGING_LEVEL(level) const LoggingLevel loggingLevel = level;
#define LOG_DEBUG debug()
#define LOG_INFO info()
#define LOG_WARNING warning()
#define LOG_ERROR error()