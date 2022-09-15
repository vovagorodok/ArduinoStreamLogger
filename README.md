# Arduino Stream Logger
Library opens posibility of logging by using ostream

## Using
Required c++17 and newer. Add to `platformio.ini`:
```
build_flags =
	-std=c++17
	-std=gnu++17
	-D LOGLEVEL_INFO
build_unflags =
	-std=gnu++11
```
Then:
```
LOG_DEBUG << "debug";
LOG_INFO << "info";
LOG_WARNING << "warning";
LOG_ERROR << "error";
```

## Side efects
In `LOGLEVEL_INFO` case when any function is called like:
```
LOG_DEBUG << foo();
```
Compiler will not optimalize it and `foo()` will be called.\
Following macro will help with that:
```
LOG_CALL_IF_DEBUG(LOG_DEBUG << foo());
```