#!/usr/bin/env python3
import argparse
import textwrap
import yaml
import os
import serial
import serial.tools.list_ports

from monitor.monitor import LogsMonitor
from monitor.monitor import start_stdscr, exit_with_error, exit_stdscr, exit_stdscr_with_error


def find_serial_port():
    ports = serial.tools.list_ports.comports()
    ports = list(filter(lambda port: port.hwid != 'n/a', ports))

    if not len(ports):
        exit_with_error("Port not found.")

    if len(ports) == 1:
        return ports[0].device

    print("Ports:")
    for index, port in enumerate(ports):
        print(f"{index}. {port.name}: {port.description}")

    user_input = input("Chose port [0]: ")

    try:
        device_num = int(user_input)
        if device_num >= len(ports) or device_num < 0:
            exit_with_error("Incorrect port number.")
    except ValueError:
        device_num = 0
        if len(user_input):
            exit_with_error("Incorrect input.")

    return ports[device_num].device


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config_path = os.path.join(script_dir, "config.yaml")
    default_logs_dir = os.path.join(script_dir, "logs")

    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""
        Tool for logs monitoring, filtering and collecting.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default=default_config_path,
                        help="Config in yaml format")
    parser.add_argument("--logs_dir", default=default_logs_dir,
                        help="Dir for logs collecting")
    args = parser.parse_args()

    try:
        config = yaml.safe_load(open(args.config))
    except FileNotFoundError as e:
        exit_with_error(e)

    try:
        port = config.get('port', None)
        if port is None:
            port = find_serial_port()
        ser = serial.Serial(
            port,
            config.get('baudrate', 115200),
            timeout=.01)
    except serial.serialutil.SerialException as e:
        exit_with_error(e)
    except KeyboardInterrupt:
        exit()

    stdscr = start_stdscr()
    logs_monitor = LogsMonitor(stdscr, config, args.logs_dir)

    try:
        while True:
            logs_monitor.pull()

            try:
                log = str(ser.readline().decode().strip('\r\n\0'))
            except UnicodeDecodeError:
                continue
            except serial.serialutil.SerialException as e:
                exit_stdscr_with_error(stdscr, e)

            if len(log):
                logs_monitor.on_log(log)

    except KeyboardInterrupt:
        exit_stdscr(stdscr)
    except ValueError as e:
        exit_stdscr_with_error(stdscr, e)


if __name__ == "__main__":
    main()
