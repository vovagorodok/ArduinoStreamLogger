#include "LogMutex.h"

#ifdef LOGGER_WITH_MUTEX
std::recursive_mutex loggerMutex{};
#endif
