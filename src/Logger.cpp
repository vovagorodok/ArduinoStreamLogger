#include "Logger.h"
#include <iostream>

namespace
{
class NullStream : public std::ostream {
public:
  NullStream() : std::ostream(nullptr) {}
  NullStream(const NullStream &) : std::ostream(nullptr) {}
};

template <class T>
const NullStream &operator<<(NullStream &&os, const T &value)
{
  return os;
}

static auto nullStream = NullStream();
}

std::ostream& trace()
{
    return loggingLevel <= LoggingLevel::Trace ? std::cout : nullStream;
}

std::ostream& debug()
{
    return loggingLevel <= LoggingLevel::Debug ? std::cout : nullStream;
}

std::ostream& info()
{
    return loggingLevel <= LoggingLevel::Info ? std::cout : nullStream;
}

std::ostream& warning()
{
    return loggingLevel <= LoggingLevel::Warning ? std::cout : nullStream;
}

std::ostream& error()
{
    return loggingLevel <= LoggingLevel::Error ? std::cout : nullStream;
}