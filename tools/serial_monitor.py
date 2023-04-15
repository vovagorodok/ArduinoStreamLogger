#!/usr/bin/env python3
import argparse
import textwrap
import yaml
import curses
import serial
import os
from enum import Enum
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Pos:
    row: int
    col: int


@dataclass
class Size:
    rows: int
    cols: int


@dataclass
class LogEntry():
    prefix: str
    show_prefix: bool
    show: bool
    colors: int


PREDEFINED_COLORS = {
    'black': curses.COLOR_BLACK,
    'red': curses.COLOR_RED,
    'green': curses.COLOR_GREEN,
    'yellow': curses.COLOR_YELLOW,
    'blue': curses.COLOR_BLUE,
    'magenta': curses.COLOR_MAGENTA,
    'cyan': curses.COLOR_CYAN,
    'white': curses.COLOR_WHITE,
    'grey': 8
}


class CursorMove(Enum):
    UP: int = 1
    DOWN: int = -1


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

    def addstr(self, text: str, row: int = 0, col: int = 0, colors: int = 0):
        start_row = self.pos.row + row
        start_col = self.pos.col + col
        max_rows = max(0, self.size.rows - row)
        max_cols = max(0, self.size.cols - col)

        lines = text.splitlines()[:max_rows]
        for line_num, line in enumerate(lines):
            self.stdscr.addstr(start_row + line_num,
                               start_col, line[:max_cols],
                               curses.color_pair(colors))

    def refresh(self, pos: Pos, visible: bool):
        self.pos = pos
        self.visible = visible

    def resize(self, size: Size):
        self.size = size


class Space(Window):
    pass


class Frame(Window):
    def __init__(self, stdscr, name: str, borders: bool, colors: int, window: Window):
        super().__init__(stdscr, Size(window.size.rows + 2, window.size.cols + 2))
        self.name = name
        self.borders = borders
        self.colors = colors
        self.window = window

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)

        if visible:
            if self.borders:
                self.add_borders()
            else:
                self.remove_borders()

            if self.name:
                self.addstr(self.name, 0, 1, self.colors)

        self.window.refresh(Pos(pos.row + 1, pos.col + 1), visible)

    def add_borders(self, l='│', r='│', t='─', b='─', tl='┌', tr='┐', bl='└', br='┘'):
        self.addstr(f"{tl}{t * (self.size.cols - 2)}{tr}", 0, 0, self.colors)
        for row in range(self.size.rows - 2):
            self.addstr(l, row + 1, 0, self.colors)
            self.addstr(r, row + 1, self.size.cols - 1, self.colors)
        self.addstr(f"{bl}{b * (self.size.cols - 2)}{br}",
                    self.size.rows - 1, 0, self.colors)

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
    def __init__(self, stdscr, size: Size, prefix: str, show_prefix: bool, colors: int, initial: str):
        super().__init__(stdscr, size)
        self.prefix = prefix
        self.show_prefix = show_prefix
        self.colors = colors
        self.log = initial

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self._redraw()

    def on_log(self, log: str):
        if log.startswith(self.prefix):
            self.log = log if self.show_prefix else log[len(self.prefix):]
            self._redraw()

    def _redraw(self):
        if self.visible:
            self.clear()
            self.addstr(self.log, 0, 0, self.colors)


class Navigation(Window):
    def __init__(self, stdscr):
        super().__init__(stdscr, Size(1, 0))

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self.clear()


class LogsFile():
    def __init__(self, logs_dir: str):
        os.makedirs(logs_dir, exist_ok=True)
        self.file = open(os.path.join(
            logs_dir, f"{datetime.now()}.log"), 'bw+')
        self.buffer = list()
        self.buffer_size = 0
        self.filter = ''
        self.held = False

    def write_log(self, log: str):
        pos = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        self._write_line(log)
        if self.held:
            self.file.seek(pos)
        elif self.filter in log:
            self.buffer.append(log)
            if len(self.buffer) > self.buffer_size:
                self.buffer.pop(0)

    def read_logs(self, size: int):
        if self.buffer_size != size:
            self.buffer_size = size
            self._update_buffer()
        return self.buffer

    def set_filter(self, filter: str):
        self.filter = filter
        self._update_buffer()

    def hold_cursor(self):
        self.held = True

    def unhold_cursor(self):
        self.held = False
        self.file.seek(0, os.SEEK_END)
        self._update_buffer()

    def move_cursor(self, move: CursorMove):
        self.hold_cursor()
        pos = self.file.tell()

        if move == CursorMove.DOWN:
            self.file.seek(0, os.SEEK_END)
            eof_pos = self.file.tell()
            pos += min(len('\n'), pos)
            pos = min(eof_pos, pos)
            for line in self._read_lines(pos, eof_pos):
                pos += len(line)
                if self.filter in line:
                    self.file.seek(pos)
                    self._update_buffer()
                    return
                pos += len('\n')
        elif move == CursorMove.UP:
            for line in self._read_lines_reverse(pos):
                pos -= len(line) + len('\n')
                pos = max(0, pos)
                if self.filter in line:
                    self.file.seek(pos)
                    self._update_buffer()
                    return

    def _update_buffer(self):
        self.buffer.clear()

        pos = self.file.tell()

        for log in self._read_lines_reverse(pos):
            if self.filter in log:
                self.buffer.insert(0, log)
            if len(self.buffer) >= self.buffer_size:
                break

        self.file.seek(pos)

    def _write_line(self, line: str):
        if self.file.tell():
            line = f"\n{line}"
        self.file.write(line.encode())

    def _read_lines(self, begin: int, end: int):
        pointer_location = begin
        buffer = bytearray()
        while pointer_location < end:
            self.file.seek(pointer_location)
            pointer_location += 1
            new_byte = self.file.read(1)
            if new_byte == b'\n':
                yield buffer.decode()
                buffer = bytearray()
            else:
                buffer.extend(new_byte)
        if len(buffer) > 0:
            yield buffer.decode()

    def _read_lines_reverse(self, begin: int, end: int = 0):
        pointer_location = begin - 1
        buffer = bytearray()
        while pointer_location >= end:
            self.file.seek(pointer_location)
            pointer_location -= 1
            new_byte = self.file.read(1)
            if new_byte == b'\n':
                yield buffer.decode()[::-1]
                buffer = bytearray()
            else:
                buffer.extend(new_byte)
        if len(buffer) > 0:
            yield buffer.decode()[::-1]


class Logs(Window):
    def __init__(self, stdscr, logs_file: LogsFile, entries: list):
        super().__init__(stdscr, Size(0, 0))
        self.entries = entries
        self.logs_file = logs_file

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self._redraw()

    def on_log(self, log: str):
        if self._should_show_log(log):
            self.logs_file.write_log(log)
            self._redraw()

    def hold_cursor(self):
        self.logs_file.hold_cursor()

    def unhold_cursor(self):
        self.logs_file.unhold_cursor()

    def move_cursor(self, move: CursorMove):
        self.logs_file.move_cursor(move)

    def _redraw(self):
        rows = self.size.rows
        if not self.visible or not rows:
            return

        self.clear()
        logs = self.logs_file.read_logs(rows)
        row = rows - len(logs)
        for line in range(len(logs)):
            self._draw_log(logs[line], row + line)

    def _draw_log(self, log: str, row: int):
        for entry in self.entries:
            if log.startswith(entry.prefix):
                text = log if entry.show_prefix else log[len(entry.prefix):]
                self.addstr(text, row, 0, entry.colors)
                return

    def _should_show_log(self, log: str):
        for entry in self.entries:
            if log.startswith(entry.prefix):
                return entry.show
        return False


class LogsMonitor():
    def __init__(self, stdscr, config, logs_dir: str):
        self.stdscr = stdscr
        self.observers = list()

        self.last_color = 0
        curses.init_pair(0, -1, -1)

        self.stdscr.clear()
        self.stdscr.refresh()

        head_config = config.get('head', None)
        self.head = self._create_window(head_config) if head_config else None

        self.logs = Logs(stdscr, LogsFile(logs_dir),
                         self._create_entries(config.get('logs', [])))
        self.nav = Navigation(stdscr)
        self.observers.append(self.logs)

        self.refresh()

    def _create_window(self, config):
        if 'space' in config:
            return self._create_space(config['space'])
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

    def _create_space(self, config):
        return Space(self.stdscr, self._create_size(config))

    def _create_frame(self, config):
        return Frame(self.stdscr,
                     config.get('name', None),
                     config.get('borders', False),
                     self._create_colors(config.get('colors', {})),
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
                        self._create_colors(config.get('colors', {})),
                        config.get('initial', ""))
        self.observers.append(status)
        return status

    def _create_size(self, config):
        return Size(config.get('rows', 0), config.get('cols', 0))

    def _create_colors(self, config):
        foreground = config.get('foreground', -1)
        background = config.get('background', -1)

        if foreground in PREDEFINED_COLORS:
            foreground = PREDEFINED_COLORS[foreground]
        if background in PREDEFINED_COLORS:
            background = PREDEFINED_COLORS[background]

        if foreground == -1 and background == -1:
            return 0

        self.last_color += 1
        curses.init_pair(self.last_color, foreground, background)
        return self.last_color

    def _create_entries(self, config):
        return list(map(lambda cfg: self._create_entry(cfg), config))

    def _create_entry(self, config):
        return LogEntry(config.get('prefix', ''),
                        config.get('show_prefix', True),
                        config.get('show', True),
                        self._create_colors(config.get('colors', {})))

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

    def on_log(self, log: str):
        for observer in self.observers:
            observer.on_log(log)

    def on_enter(self):
        self.logs.hold_cursor()

    def on_escape(self):
        self.logs.unhold_cursor()

    def move_cursor(self, move: CursorMove):
        self.logs.move_cursor(move)


def main(stdscr):
    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""
        Tool for logs monitoring, filtering and collecting.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default="config.yaml",
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

    curses.start_color()
    curses.use_default_colors()
    stdscr.nodelay(True)
    logs_monitor = LogsMonitor(stdscr, config, args.logs_dir)

    try:
        while True:
            ch = stdscr.getch()
            if ch == curses.KEY_RESIZE:
                logs_monitor.refresh()
            if ch == 13 or ch == ord('\n'):
                logs_monitor.on_enter()
            if ch == 27:
                logs_monitor.on_escape()
            if ch == curses.KEY_UP:
                logs_monitor.move_cursor(CursorMove.UP)
            if ch == curses.KEY_DOWN:
                logs_monitor.move_cursor(CursorMove.DOWN)
            if ch == ord('q'):
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
                logs_monitor.on_log(log)

    except KeyboardInterrupt:
        exit()


curses.wrapper(main)
