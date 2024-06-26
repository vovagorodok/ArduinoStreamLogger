# Arduino Stream Logger
Library opens posibility of logging by using ostream.  
When log level is disabled (by adding `-D LOG_LEVEL_DISABLED` or removing `-D LOG_LEVEL_..`) then all strings, operators calls, etc. will be optimized/removed from binary.

## Using
Use as follows:
```
#include <Logger.h>
...
LOG_DEBUG << "debug";
LOG_INFO << "info";
LOG_WARNING << "warning";
LOG_ERROR << "error";
```

## Optimization aspects
Compiler will not optimize function calls.  
For example, in case of `LOG_LEVEL_INFO` and debug with function call:
```
LOG_DEBUG << foo();
```
Compiler optimize only logging, but `foo()` will be called.  
Following macro will help to optimize all:
```
LOG_CALL_DEBUG(<< foo());
```

## Additional format options
Disable prefix:
```
build_flags =
	-D LOG_FORMAT_WITHOUT_PREFIX
```
Custom separator:
```
build_flags =
	-D LOG_FORMAT_SEPARATOR='"\\\\"'
```
Default separator is `": "`.

## Configuration
Library require c++17 or newer.  
For PlatformIO. Add to `platformio.ini`:
```
build_flags =
	-std=c++17
	-std=gnu++17
	-D LOG_LEVEL_INFO
build_unflags =
	-std=gnu++11
```

For Arduino IDE. At boards package installation folder create `platform.local.txt`:
```
compiler.cpp.extra_flags=-std=c++17 -D LOG_LEVEL_INFO
```