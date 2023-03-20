# Arduino Stream Logger
Library opens posibility of logging by using ostream.\
When log level is disabled (by adding `-D LOG_LEVEL_DISABLED` or removing `-D LOG_LEVEL_..`) then all strings, operators calls, etc. will be optimalized/removed from binary.

## Using
Required c++17 or newer. Add to `platformio.ini`:
```
build_flags =
	-std=c++17
	-std=gnu++17
	-D LOG_LEVEL_INFO
build_unflags =
	-std=gnu++11
```
Then in code:
```
LOG_DEBUG << "debug";
LOG_INFO << "info";
LOG_WARNING << "warning";
LOG_ERROR << "error";
```

## Optomization aspects
Compiler will not optimalize function calls.\
For example, in case of `LOG_LEVEL_INFO` and debug with function call:
```
LOG_DEBUG << foo();
```
Compiler optimalize only logging, but `foo()` will be called.\
Following macro will help optimalize all:
```
LOG_CALL_IF_DEBUG(LOG_DEBUG << foo());
```
