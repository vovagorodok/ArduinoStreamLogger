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
    show: bool
    colors: int


DEFAULT_COLORS = 0

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

    def clear(self, colors: int = DEFAULT_COLORS):
        spaces = ' ' * self.size.cols
        for row in range(self.size.rows):
            self.stdscr.addstr(self.pos.row + row,
                               self.pos.col,
                               spaces,
                               curses.color_pair(colors))

    def addstr(self, text: str, row: int = 0, col: int = 0, colors: int = DEFAULT_COLORS):
        start_row = self.pos.row + row
        start_col = self.pos.col + col
        max_rows = max(0, self.size.rows - row)
        max_cols = max(0, self.size.cols - col)

        lines = text.splitlines()[:max_rows]
        for line_num, line in enumerate(lines):
            self.stdscr.addstr(start_row + line_num,
                               start_col,
                               line[:max_cols],
                               curses.color_pair(colors))

    def refresh(self, pos: Pos, visible: bool):
        self.pos = pos
        self.visible = visible

    def resize(self, size: Size):
        self.size = size


class Space(Window):
    def __init__(self, stdscr, size: Size, colors: int):
        super().__init__(stdscr, size)
        self.colors = colors

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        if visible:
            self.clear(self.colors)


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


class Label(Window):
    def __init__(self,
                 stdscr,
                 size: Size,
                 colors: int,
                 text: str,
                 wrap_around: bool):
        super().__init__(stdscr, size)
        self.colors = colors
        self.text = text
        self.wrap_around = wrap_around
        self._format_text()

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self._redraw()

    def _format_text(self):
        col = 0
        formated_text = ''
        for ch in self.text:
            if self.wrap_around and col >= self.size.cols:
                col = 0
                formated_text += '\n'
            formated_text += ch
            col += 1
        self.text = formated_text

    def _redraw(self):
        if self.visible:
            self.clear(self.colors)
            self.addstr(self.text, 0, 0, self.colors)


class Status(Window):
    def __init__(self,
                 stdscr,
                 size: Size,
                 prefix: str,
                 show_prefix: bool,
                 colors: int,
                 initial: str,
                 wrap_around: bool,
                 insert_spaces: bool):
        super().__init__(stdscr, size)
        self.prefix = prefix
        self.show_prefix = show_prefix
        self.colors = colors
        self.log = initial
        self.wrap_around = wrap_around
        self.insert_spaces = insert_spaces

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self._redraw()

    def on_log(self, log: str):
        if log.startswith(self.prefix):
            self.log = log if self.show_prefix else log[len(self.prefix):]
            self._format_log()
            self._redraw()

    def _format_log(self):
        col = 0
        formated_log = ''
        for ch in self.log:
            if self.wrap_around and col >= self.size.cols:
                col = 0
                formated_log += '\n'
            formated_log += ch
            col += 1
            if self.insert_spaces:
                if self.wrap_around and col >= self.size.cols:
                    col = 0
                    formated_log += '\n'
                else:
                    formated_log += ' '
                    col += 1
        self.log = formated_log

    def _redraw(self):
        if self.visible:
            self.clear(self.colors)
            self.addstr(self.log, 0, 0, self.colors)


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

    def search(self, text: str):
        pos = self.file.tell()

        next_pos = pos
        self.file.seek(0, os.SEEK_END)
        eof_pos = self.file.tell()
        next_pos += min(len('\n'), next_pos)
        next_pos = min(eof_pos, next_pos)
        for line in self._read_lines(next_pos, eof_pos):
            next_pos += len(line)
            if self.filter in line and text in line:
                self.file.seek(next_pos)
                self._update_buffer()
                return
            next_pos += len('\n')
        next_pos = 0
        for line in self._read_lines(next_pos, pos):
            next_pos += len(line)
            if self.filter in line and text in line:
                self.file.seek(next_pos)
                self._update_buffer()
                return
            next_pos += len('\n')

        self.file.seek(next_pos)

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
    def __init__(self, stdscr, logs_file: LogsFile, entries: list, show_prefix: bool):
        super().__init__(stdscr, Size(0, 0))
        self.entries = entries
        self.logs_file = logs_file
        self.show_prefix = show_prefix

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
        self._redraw()

    def move_cursor(self, move: CursorMove):
        self.logs_file.move_cursor(move)
        self._redraw()

    def set_filter(self, filter: str):
        self.logs_file.set_filter(filter)
        self._redraw()

    def search(self, text: str):
        self.logs_file.search(text)
        self._redraw()

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
                text = log if self.show_prefix else log[len(entry.prefix):]
                self.addstr(text, row, 0, entry.colors)
                return

    def _should_show_log(self, log: str):
        for entry in self.entries:
            if log.startswith(entry.prefix):
                return entry.show
        return False


class NavigationButton(Window):
    def __init__(self, stdscr, size: Size, key: str, text: str, colors: int):
        super().__init__(stdscr, size)
        self.key = key
        self.text = text
        self.colors = colors

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        if self.visible:
            self.addstr(self.key)
            self.addstr(self.text, 0, len(self.key), self.colors)


class Navigation(Window):
    def __init__(self, stdscr, logs: Logs, colors: int):
        super().__init__(stdscr, Size(1, 0))
        self.logs = logs
        self.colors = colors
        self.stoped = False
        self.searching = False
        self.search = ''
        self.filtering = False
        self.filter = ''
        self.stop_button = self._create_button('Enter', 'Stop'.ljust(7))
        self.stop_button = self._create_button('Esc', 'Resume'.ljust(7))
        self.edit_buttons = [
            self._create_button('Enter', 'Apply'.ljust(7)),
            self._create_button('Esc', 'Resume'.ljust(7))]
        self.main_buttons = [
            self._create_button('F3', 'Search'.ljust(7)),
            self._create_button('F4', 'Filter'.ljust(7)),
            self._create_button('F10', 'Quit'.ljust(7))]

    def _create_button(self, key: str, text: str):
        rows = len(key) + len(text)
        return NavigationButton(self.stdscr, Size(1, rows), key, text, self.colors)

    def refresh(self, pos: Pos, visible: bool):
        super().refresh(pos, visible)
        self._redraw()

    def pull(self, ch: int):
        if ch == curses.KEY_ENTER or ch == 13 or ch == ord('\n'):
            if self.filtering:
                self.filtering = False
                self.logs.set_filter(self.filter)
            elif self.searching:
                self.searching = False
                self.logs.search(self.search)
            else:
                self.logs.hold_cursor()
                self.stoped = True
            self._redraw()
        elif ch == 27:
            if self.filtering:
                self.filtering = False
                self.filter = ''
                self.logs.set_filter(self.filter)
            else:
                self.logs.unhold_cursor()
                self.stoped = False
            self._redraw()
        elif ch == curses.KEY_UP:
            self.logs.move_cursor(CursorMove.UP)
            self.stoped = True
            self._redraw()
        elif ch == curses.KEY_DOWN:
            self.logs.move_cursor(CursorMove.DOWN)
            self.stoped = True
            self._redraw()
        elif ch == curses.KEY_F3:
            self.searching = True
            self.filtering = False
            self.logs.hold_cursor()
            self.stoped = True
            self._redraw()
        elif ch == curses.KEY_F4:
            self.filtering = True
            self.searching = False
            self._redraw()
        elif ch == curses.KEY_F10:
            exit()

        if self.filtering:
            if ch == curses.KEY_BACKSPACE:
                self.filter = self.filter[:-1]
                self._redraw()
            elif ch >= ord('!') and ch <= ord('~'):
                self.filter += chr(ch)
                self._redraw()
        elif self.searching:
            if ch == curses.KEY_BACKSPACE:
                self.search = self.search[:-1]
                self._redraw()
            elif ch >= ord('!') and ch <= ord('~'):
                self.search += chr(ch)
                self._redraw()
        else:
            if ch == ord('q'):
                exit()

    def _redraw(self):
        col = self._draw_panel()
        free_cols = max(0, self.size.cols - col)
        if free_cols:
            self.addstr(' ' * free_cols, 0, col, self.colors)
        self.stdscr.refresh()

    def _draw_panel(self):
        buttons = list()
        if self.filtering or self.searching:
            buttons += self.edit_buttons
        else:
            buttons.append(
                self.resume_button if self.stoped else self.stop_button)
            buttons += self.main_buttons

        col = self.pos.col
        max_cols = self.size.cols

        if col + 2 > max_cols:
            return col
        self.addstr(' ' * 2, 0, col, self.colors)
        col += 2

        for button in buttons:
            if col + button.size.cols > max_cols:
                return col
            button.refresh(Pos(self.pos.row, col), self.visible)
            col += button.size.cols

        if not self.filtering and not self.searching:
            return col

        if col + 2 > max_cols:
            return col
        self.addstr(' ' * 2, 0, col)
        col += 2

        edit_prefix = 'Filter: ' if self.filtering else 'Search: '
        if col + len(edit_prefix) > max_cols:
            return col
        self.addstr(edit_prefix, 0, col, self.colors)
        col += len(edit_prefix)

        free_cols = max_cols - col
        if free_cols <= 0:
            return col
        edit_text = self.filter if self.filtering else self.search
        visible_text = edit_text[-free_cols:].ljust(free_cols)
        self.addstr(visible_text, 0, col, self.colors)
        col += len(visible_text)

        return col


class LogsMonitor():
    def __init__(self, stdscr, config, logs_dir: str):
        self.stdscr = stdscr
        self.observers = list()

        self.last_color = 0
        curses.init_pair(DEFAULT_COLORS, -1, -1)

        self.stdscr.clear()
        self.stdscr.refresh()

        head_config = config.get('head', None)
        self.head = self._create_window(head_config) if head_config else None
        self.head_cleaner = Space(
            self.stdscr, self.head.size, DEFAULT_COLORS) if self.head else None

        entries = self._create_entries(config.get(
            'logs', [{'prefix': '', 'show': True}]))
        self.logs = Logs(
            stdscr, LogsFile(logs_dir), entries, config.get('show_prefix', True))
        self.observers.append(self.logs)

        nav_colors = self._create_colors(config.get(
            'navigation_colors', {'foreground': 'black', 'background': 'cyan'}))
        self.nav = Navigation(stdscr, self.logs, nav_colors)

        self.refresh()

    def _create_window(self, config):
        if 'space' in config:
            return self._create_space(config['space'])
        elif 'frame' in config:
            return self._create_frame(config['frame'])
        elif 'row' in config:
            return self._create_row(config['row'])
        elif 'col' in config:
            return self._create_col(config['col'])
        elif 'label' in config:
            return self._create_label(config['label'])
        elif 'status' in config:
            return self._create_status(config['status'])
        else:
            raise ValueError(f"Invalid config\n {config}")

    def _create_windows(self, config):
        return list(map(lambda cfg: self._create_window(cfg), config))

    def _create_space(self, config):
        return Space(self.stdscr,
                     self._create_size(config['size']),
                     self._create_colors(config.get('colors', {})))

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

    def _create_label(self, config):
        return Label(self.stdscr,
                     self._create_size(config['size']),
                     self._create_colors(config.get('colors', {})),
                     config.get('text', ""),
                     config.get('wrap_around', False))

    def _create_status(self, config):
        status = Status(self.stdscr,
                        self._create_size(config['size']),
                        config.get('prefix', ""),
                        config.get('show_prefix', False),
                        self._create_colors(config.get('colors', {})),
                        config.get('initial', ""),
                        config.get('wrap_around', False),
                        config.get('insert_spaces', False))
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
            return DEFAULT_COLORS

        self.last_color += 1
        curses.init_pair(self.last_color, foreground, background)
        return self.last_color

    def _create_entries(self, config):
        return list(map(lambda cfg: self._create_entry(cfg), config))

    def _create_entry(self, config):
        return LogEntry(config.get('prefix', ''),
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
                cleaner_size = Size(self.head_cleaner.size.rows, cols)
                self.head_cleaner.resize(cleaner_size)
                self.head_cleaner.refresh(Pos(0, 0), True)
                self.head.refresh(Pos(0, 0), True)
            else:
                self.head.refresh(Pos(0, 0), False)
        else:
            enable_head = False

        logs_pos = self.head.size.rows if enable_head else 0
        self.logs.resize(Size(free_size, cols))
        self.logs.refresh(Pos(logs_pos, 0), free_size)

        self.stdscr.refresh()

    def on_log(self, log: str):
        for observer in self.observers:
            observer.on_log(log)
        self.stdscr.refresh()

    def pull(self):
        ch = self.stdscr.getch()
        if ch == curses.KEY_RESIZE:
            self.refresh()
        else:
            self.nav.pull(ch)


def exit_with_error(error):
    curses.endwin()
    print(f"\n{error}")
    exit()


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
        exit_with_error(e)

    try:
        ser = serial.Serial(
            config.get('port', '/dev/ttyUSB0'),
            config.get('baudrate', 115200),
            timeout=.01)
    except serial.serialutil.SerialException as e:
        exit_with_error(e)

    curses.start_color()
    curses.use_default_colors()
    stdscr.nodelay(True)
    logs_monitor = LogsMonitor(stdscr, config, args.logs_dir)

    try:
        while True:
            logs_monitor.pull()

            try:
                log = str(ser.readline().decode().strip('\r\n\0'))
            except UnicodeDecodeError:
                continue
            except serial.serialutil.SerialException as e:
                exit_with_error(e)

            if len(log):
                logs_monitor.on_log(log)

    except KeyboardInterrupt:
        exit()
    except ValueError as e:
        exit_with_error(e)


curses.wrapper(main)
