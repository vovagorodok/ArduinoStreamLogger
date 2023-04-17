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
You can easely run from your project. Add to your `tools` content of `tools\examples` and modify it.

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
 - `port`: optional. Default `/dev/ttyUSB0`
 - `baudrate`: optional. Default `115200`
 - `show_prefix`: optional. Default `true`
 - `navigation_colors`: optional. See colors structure

Head:
 - `head`: optional. Contains tree window structures

 Logs:
 - `logs`: optional. Contains list of log entries

## General structures:
Colors:
 - `foreground`: optional. Example `green` or `2`
 - `background`: optional

Size:
 - `rows`: optional. Default `0`
 - `cols`: optional. Default `0`

Log Entry:
 - `prefix`: optional. Example `INF: `. Default empty
 - `show`: optional. Show and store log. Default `0`
 - `colors`: optional

## Window structures:
Space (empty space):
 - `size`: mandatory
 - `colors`: optional

Frame (frame around window):
 - `name`: optional. Default empty
 - `borders`: optional. Enable borders. Default `false`
 - `colors`: optional
 - `window`: mandatory. Window inside frame

Label (static text):
 - `size`: mandatory
 - `colors`: optional
 - `text`: optional. Default empty
 - `wrap_around`: optional. Move to new line if text is to long. Default `false`

Status (status of specific log):
 - `size`: mandatory
 - `prefix`: optional. Example `INF: `. Default empty
 - `show_prefix`: optional. Default `false`
 - `colors`: optional
 - `initial`: optional. Example `wait for data..`. Default empty
 - `wrap_around`: optional. Move to new line if log is to long. Default `false`
 - `insert_spaces`: optional. Insert spaces between each char. Default `false`

Row (row of window structures):
 - list of window structures

Col (column of window structures):
 - list of window structures