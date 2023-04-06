
import curses


def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLORS):
        curses.init_pair(i + 1, i, -1)
        stdscr.addstr(f"{i - 1} ", curses.color_pair(i))
    stdscr.getch()


curses.wrapper(main)
