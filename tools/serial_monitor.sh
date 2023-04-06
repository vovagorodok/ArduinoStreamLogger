#!/bin/bash

SCRIPT_DIR=$( cd $( dirname $0 ) && pwd )
SCRIPT_PATH=$SCRIPT_DIR/serial_monitor.py
CONFIG_PATH=$SCRIPT_DIR/config.yaml
LOGS_DIR=$SCRIPT_DIR/../logs

python3 $SCRIPT_PATH --config=$CONFIG_PATH --logs_dir=$LOGS_DIR