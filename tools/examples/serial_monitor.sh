#!/bin/bash

SCRIPT_DIR=$( cd $( dirname $0 ) && pwd )
VSCODE_LAUNCH_PATH=$SCRIPT_DIR/../.vscode/launch.json
CURRENT_ENV=$( awk '/projectEnvName/ {print $2; exit}' $VSCODE_LAUNCH_PATH | sed 's/[",]//g' )
SCRIPT_PATH=$SCRIPT_DIR/../.pio/libdeps/$CURRENT_ENV/ArduinoStreamLogger/tools/serial_monitor.py
CONFIG_PATH=$SCRIPT_DIR/config.yaml
LOGS_DIR=$SCRIPT_DIR/logs

python3 $SCRIPT_PATH --config=$CONFIG_PATH --logs_dir=$LOGS_DIR