#!/usr/bin/env python3
import argparse
import textwrap
import yaml
import curses
import serial
from dataclasses import dataclass


@dataclass
class Pos:
    row: int
    col: int


@dataclass
class Size:
    rows: int
    cols: int


class Window():
    def __init__(self, stdscr, size: Size):
        self.stdscr = stdscr
        self.size = size
        self.pos = Pos(0, 0)
        self.visible = False

    def clear(self):
        spaces = ' ' * self.size.cols
        for row in range(self.size.rows):
            self.stdscr.addstr(self.pos.row + row, self.pos.col, spaces)

    def addstr(self, text: str, row: int = 0, col: int = 0):
        start_row = self.pos.row + row
        start_col = self.pos.col + col
        max_rows = max(0, self.size.rows - row)
        max_cols = max(0, self.size.cols - col)

        lines = text.splitlines()[:max_rows]
        for line_num, line in enumerate(lines):
            self.stdscr.addstr(start_row + line_num,
                               start_col, line[:max_cols])

    def refresh(self, pos: Pos, visible: bool):
        self.pos = pos
        self.visible = visible

    def resize(self, size: Size):
        self.size = size


class Frame(Window):
    def __init__(self, stdscr, name: str, borders: bool, window: Window):
        super().__init__(stdscr, Size(window.size.rows + 2, window.size.cols + 2))
        self.name = name
        self.borders = borders
        self.window = window

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)

        if visible:
            if self.borders:
                self.add_borders()
            else:
                self.remove_borders()

            if self.name:
                self.addstr(self.name, 0, 1)

        self.window.refresh(Pos(pos.row + 1, pos.col + 1), visible)

    def add_borders(self, l='│', r='│', t='─', b='─', tl='┌', tr='┐', bl='└', br='┘'):
        self.addstr(f"{tl}{t * (self.size.cols - 2)}{tr}")
        for row in range(self.size.rows - 2):
            self.addstr(l, row + 1, 0)
            self.addstr(r, row + 1, self.size.cols - 1)
        self.addstr(f"{bl}{b * (self.size.cols - 2)}{br}", self.size.rows - 1)

    def remove_borders(self):
        self.add_borders(' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ')


class Row(Window):
    def __init__(self, stdscr, windows: list):
        super().__init__(stdscr, Size(max(map(lambda window: window.size.rows, windows)),
                                      sum(map(lambda window: window.size.cols, windows))))
        self.windows = windows

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        col = pos.col
        for window in self.windows:
            window.refresh(Pos(pos.row, col), visible)
            col += window.size.cols


class Col(Window):
    def __init__(self, stdscr, windows: list):
        super().__init__(stdscr, Size(sum(map(lambda window: window.size.rows, windows)),
                                      max(map(lambda window: window.size.cols, windows))))
        self.windows = windows

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        row = pos.row
        for window in self.windows:
            window.refresh(Pos(row, pos.col), visible)
            row += window.size.rows


class Status(Window):
    def __init__(self, stdscr, size: Size, prefix: str, show_prefix: bool, initial: str):
        super().__init__(stdscr, size)
        self.prefix = prefix
        self.show_prefix = show_prefix
        self.log = initial

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self._redraw()

    def onLog(self, log: str):
        if log.startswith(self.prefix):
            self.log = log if self.show_prefix else log[len(self.prefix):]
            self._redraw()

    def _redraw(self):
        if self.visible:
            self.clear()
            self.addstr(self.log)


class Navigation(Window):
    def __init__(self, stdscr, size: Size):
        super().__init__(stdscr, size)

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self.clear()


class Logs(Window):
    def __init__(self, stdscr, size: Size):
        super().__init__(stdscr, size)
        self.logs = list()

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self._redraw()

    def onLog(self, log: str):
        self.logs.append(log)
        self._redraw()

    def _redraw(self):
        rows = self.size.rows
        if not self.visible or not rows:
            return

        self.clear()
        show = self.logs[-rows:]
        self.addstr('\n'.join(show), rows - len(show))


class LogsMonitor():
    def __init__(self, stdscr, config):
        self.stdscr = stdscr
        self.observers = list()
        self.stdscr.clear()
        self.stdscr.refresh()

        head_config = config.get('head', None)
        self.head = self._create_window(head_config) if head_config else None

        self.logs = Logs(stdscr, Size(0, 0))
        self.nav = Navigation(stdscr, Size(1, 0))
        self.observers.append(self.logs)

        self.refresh()

    def _create_window(self, config):
        if 'frame' in config:
            return self._create_frame(config['frame'])
        if 'row' in config:
            return self._create_row(config['row'])
        if 'col' in config:
            return self._create_col(config['col'])
        if 'status' in config:
            return self._create_status(config['status'])
        return None

    def _create_windows(self, config):
        return list(map(lambda cfg: self._create_window(cfg), config))

    def _create_frame(self, config):
        return Frame(self.stdscr,
                     config.get('name', None),
                     config.get('borders', False),
                     self._create_window(config['window']))

    def _create_row(self, config):
        return Row(self.stdscr, self._create_windows(config))

    def _create_col(self, config):
        return Col(self.stdscr, self._create_windows(config))

    def _create_status(self, config):
        status = Status(self.stdscr,
                        self._create_size(config['size']),
                        config.get('prefix', ""),
                        config.get('show_prefix', False),
                        config.get('initial', ""))
        self.observers.append(status)
        return status

    def _create_size(self, config):
        return Size(config[0], config[1])

    def refresh(self):
        rows, cols = self.stdscr.getmaxyx()

        free_size = max(0, rows - self.nav.size.rows)

        self.nav.resize(Size(self.nav.size.rows, max(0, cols - 1)))
        self.nav.refresh(Pos(free_size, 0), True)

        if self.head:
            enable_head = cols >= self.head.size.cols and free_size >= self.head.size.rows
            if enable_head:
                free_size -= self.head.size.rows
                self.head.refresh(Pos(0, 0), True)
            else:
                self.head.refresh(Pos(0, 0), False)
        else:
            enable_head = False

        logs_pos = self.head.size.rows if enable_head else 0
        self.logs.resize(Size(free_size, cols))
        self.logs.refresh(Pos(logs_pos, 0), True)

        self.stdscr.refresh()

    def onLog(self, log: str):
        for observer in self.observers:
            observer.onLog(log)


def main(stdscr):
    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""
        Tool for logs monitoring, filtering and collecting.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default="tools/config.yaml",
                        help="Config in yaml format")
    parser.add_argument("--logs_dir", default="logs",
                        help="Dir for logs collecting")
    args = parser.parse_args()

    try:
        config = yaml.safe_load(open(args.config))
    except FileNotFoundError as e:
        curses.endwin()
        print(e)
        exit()

    try:
        ser = serial.Serial(config['port'], config['baudrate'], timeout=.01)
    except serial.serialutil.SerialException as e:
        curses.endwin()
        print(e)
        exit()

    stdscr.nodelay(True)
    logs_monitor = LogsMonitor(stdscr, config)

    while True:
        ch = stdscr.getch()
        if ch == curses.KEY_RESIZE or ch == curses.KEY_RESUME:
            logs_monitor.refresh()
        if ch == ord('q'):
            ser.close()
            exit()

        try:
            log = str(ser.readline().decode().strip('\r\n'))
        except UnicodeDecodeError:
            continue
        except serial.serialutil.SerialException as e:
            curses.endwin()
            print(e)
            exit()

        if len(log):
            logs_monitor.onLog(log)


curses.wrapper(main)
