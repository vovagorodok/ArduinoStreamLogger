#!/usr/bin/env python3
import argparse
import textwrap
import yaml
import os
import asyncio

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

from monitor import uuids
from monitor.utils import is_linux, is_fedora
from monitor.monitor import LogsMonitor
from monitor.monitor import start_stdscr, exit_with_error, exit_stdscr, exit_stdscr_with_error


async def scan_devices(service_uuid: str, timeout=5.0):
    devices_dict = await BleakScanner.discover(timeout=timeout, return_adv=True)

    for dev, adv in devices_dict.values():
        if service_uuid.lower() in adv.service_uuids:
            yield dev


async def acquire_mtu(client: BleakClient):
    if not is_linux():
        return

    # issue: https://github.com/hbldh/bleak/issues/1471
    if is_fedora():
        return

    from bleak.backends.bluezdbus.client import BleakClientBlueZDBus
    if type(client._backend) is not BleakClientBlueZDBus:
        return
    
    # in Linux acquire mtu should be called in order to have more than 23
    await client._backend._acquire_mtu()


async def connect(dev):
    client = BleakClient(dev)

    print(f"Connecting to {dev.name}")
    await client.connect()
    if not client.is_connected:
        exit_with_error("Connection failed.")

    await acquire_mtu(client)

    service = client.services.get_service(uuids.BLE_SERIAL_SERVICE_UUID)
    tx_char = service.get_characteristic(uuids.BLE_SERIAL_CHARACTERISTIC_UUID_TX)
    rx_char = service.get_characteristic(uuids.BLE_SERIAL_CHARACTERISTIC_UUID_RX)

    return client, tx_char, rx_char


async def find_ble_device(service_uuid: str):
    devices = list()

    print("Devices:")
    async for device in scan_devices(service_uuid):
        print(f"{len(devices)}. [{device.address}] {device.name}")
        devices.append(device)

    if not len(devices):
        exit_with_error("Device not found.")

    user_input = input("Chose device [0]: ")

    try:
        device_num = int(user_input)
        if device_num >= len(devices) or device_num < 0:
            exit_with_error("Incorrect device number.")
    except ValueError:
        device_num = 0
        if len(user_input):
            exit_with_error("Incorrect input.")

    return devices[device_num]


async def main():
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
    parser.add_argument("--service_uuid", default=uuids.BLE_SERIAL_SERVICE_UUID,
                        help="Service UUID")
    args = parser.parse_args()

    try:
        config = yaml.safe_load(open(args.config))
    except FileNotFoundError as e:
        exit_with_error(e)

    try:
        device = await find_ble_device(args.service_uuid)
        client, tx_char, rx_char = await connect(device)
    except (KeyboardInterrupt, asyncio.CancelledError):
        exit()
    except BleakError as e:
        exit_with_error(e)

    stdscr = start_stdscr()
    logs_monitor = LogsMonitor(stdscr, config, args.logs_dir)

    # issue: https://github.com/hbldh/bleak/issues/1501
    queue = asyncio.Queue(100)
    async def callback(char, array):
        try:
            queue.put_nowait(array)
        except asyncio.QueueFull:
            exit_stdscr_with_error(stdscr, "Queue is full.")
    await client.start_notify(rx_char, callback)

    try:
        while True:
            logs_monitor.pull()

            try:
                log = str(queue.get_nowait(), 'utf-8').strip('\r\n\0')
            except asyncio.QueueEmpty:
                log = str()
            except UnicodeDecodeError:
                continue

            if len(log):
                logs_monitor.on_log(log)
            else:
                await asyncio.sleep(0.01)

    except (KeyboardInterrupt, asyncio.CancelledError):
        exit_stdscr(stdscr)
    except ValueError as e:
        exit_stdscr_with_error(stdscr, e)


if __name__ == "__main__":
    asyncio.run(main())
