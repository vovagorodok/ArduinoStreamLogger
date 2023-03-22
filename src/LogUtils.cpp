#include "LogUtils.h"

#ifdef LOGGER_WITH_MUTEX
std::mutex loggerMutex{};
#endif
