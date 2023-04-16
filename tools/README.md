# Serial monitor
Console application to display and store logs.\
Just run:
```
./tools/serial_monitor.sh
```
or
```
python3 serial_monitor.py --config=<path to config yaml>
```
You can easely run from your project. See `tools\examples` how to do that.

## Colors
Each color has integer value.\
Set `-1` in order to use default color.\
Predefined colors:
```
black   0
red     1
green   2
yellow  3
blue    4
magenta 5
cyan    6
white   7
```
Color plate can be extended to 256 colors. In order to check each color number run `show_colors.py`.

## Custom config:
Config can contain general, head and logs parameters.\
General:
 - `port`: mandatory. Example `/dev/ttyUSB0`
 - `baudrate`: mandatory. Example `115200`
 - `show_prefix`: optional. Default `true`
 - `navigation_colors`: optional. See colors structure

Head:
 - `head`: optional. Contains tree window structures

 Logs:
 - `logs`: optional. Contains list of log entries

## General structures:
Colors:
```
 - `foreground`: optional. Example `green` or `2`
 - `background`: optional.
```