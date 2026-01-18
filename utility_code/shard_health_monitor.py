#!/usr/bin/env python3
"""A shard health monitor for the terminal

Based on a Python asyncio curses template by davesteele:
https://gist.github.com/davesteele/8838f03e0594ef11c89f77a7bca91206
"""

import argparse
import asyncio
from abc import ABC, abstractmethod
import curses
import _curses
import uuid
from lib_py3.lib_sockets import SocketManager
from lib_py3.shard_health import ShardHealth


START_COLOR = 16
START_COLOR_PAIR = 2
HEALTH_STEPS = 64


YELLOW_HEALTH = ShardHealth.default_target_health()
ZERO_HEALTH = ShardHealth.zero_health()


HEADER = (
    "Type", "Shard", "Health", "Memory", "Idle Time",
    "G1 Old", "G1 Young", "G1 Concurrent", "G1 Overall",
)


class Display(ABC):
    def __init__(self, stdscr: "_curses._CursesWindow"):
        self.stdscr = stdscr
        self.refresh: bool = False
        self.done: bool = False


    @abstractmethod
    def make_display(self) -> None:
        pass


    @abstractmethod
    def handle_char(self, char: int) -> None:
        pass


    def set_exit(self) -> None:
        self.done = True


    async def run(self) -> None:
        curses.curs_set(0)
        self.stdscr.nodelay(True)

        self.make_display()

        while not self.done:
            char = self.stdscr.getch()
            if char == curses.ERR:
                try:
                    if self.refresh:
                        self.refresh = False
                        self.make_display()
                    await asyncio.sleep(0.1)
                except asyncio.exceptions.CancelledError:
                    self.done = True
            elif char == curses.KEY_RESIZE:
                self.make_display()
            else:
                self.handle_char(char)


class ShardHealthMonitorDisplay(Display):
    def __init__(self, stdscr: "_curses._CursesWindow", host: str):
        super().__init__(stdscr)
        self.host = host
        self.queue_name = f'shard-health-monitor-{uuid.uuid4()}'
        self.socket = None

        self.background = 0
        self.colors = {}
        self.color_pairs = {}


    def make_display(self) -> None:
        maxy, maxx = self.stdscr.getmaxyx()
        self.stdscr.attrset(self.background)
        self.stdscr.erase()

        remote_heartbeats = self.socket.remote_heartbeats()

        self.stdscr.box()
        table = TableFormatter(HEADER, TextComponent(' | '))
        for source in sorted(remote_heartbeats, key=self.shard_sort_key):
            self.add_health_line(table, source)
        table.show_table(self.stdscr, 1, 1)

        self.stdscr.refresh()


    def handle_char(self, char: int) -> None:
        if chr(char) == "q":
            self.set_exit()


    def socket_callback(self, message):
        if message.get("pluginData", {}).get("monumentanetworkrelay", None) is not None:
            self.refresh = True


    async def run(self) -> None:
        self.init_colors()
        self.socket = SocketManager(self.host, self.queue_name, durable=False, callback=self.socket_callback, track_heartbeats=True)
        self.socket.send_heartbeat()
        await super().run()


    def add_health_line(self, table, source) -> None:
        shard_type = self.socket.shard_type(source)
        health_data = self.socket.shard_health_data(source)

        row = [shard_type, source]
        row.append(self.colored_stat(health_data, ShardHealth.health_score))
        row.append(self.colored_stat(health_data, ShardHealth.memory_health))
        row.append(self.colored_stat(health_data, ShardHealth.tick_health))

        table.add_row(row)


    def shard_sort_key(self, source):
        shard_type = self.socket.shard_type(source)
        return (shard_type, source)


    def colored_stat(self, health, func):
        value = func(health)
        return TextComponent(f'{value:4.2f}', self.mix_colors(func(YELLOW_HEALTH), value))


    def mix_colors(self, mid_value, actual_value):
        if actual_value <= mid_value:
            return self.mix_sub_colors(0.0, HEALTH_STEPS / 2.0, 0.0, mid_value, actual_value)
        else:
            return self.mix_sub_colors(HEALTH_STEPS / 2.0, HEALTH_STEPS, mid_value, 1.0, actual_value)


    def mix_sub_colors(
        self,
        min_color,
        max_color,
        min_value,
        max_value,
        actual_value
    ):
        max_min_diff = max_value - min_value
        if min_value <= 0.0:
            return int(min_color)

        percent_max_color = (actual_value - min_value) / max_min_diff
        percent_min_color = 1.0 - percent_max_color

        color_index = round(percent_min_color * min_color + percent_max_color * max_color)

        return self.color_attr(color_index)


    def init_colors(self):
        # Background colors from plugin health monitor, converted to curses-style
        self.background = self._add_color(
            1000 * 0x2E // 0xFF,
            1000 * 0x34 // 0xFF,
            1000 * 0x36 // 0xFF,
        )

        self._add_color_pair(
            "default",
            self.background,
            self._add_color(1000, 1000, 1000),
        )
        TextComponent.set_default_color(self.color_attr("default"))

        for health in range(HEALTH_STEPS+1):
            self._add_color_pair(
                health,
                self.background,
                self._add_color(
                    min(1000, 2000 * (HEALTH_STEPS - health) // HEALTH_STEPS), # red
                    min(1000, 2000 *                 health  // HEALTH_STEPS), # green
                    0 # blue
                ),
            )


    def _add_color(self, r, g, b):
        index = START_COLOR + len(self.colors)
        curses.init_color(index, r, g, b)
        self.colors[index] = (r, g, b)
        return index


    def _add_color_pair(self, label, bg, fg):
        index = START_COLOR_PAIR + len(self.color_pairs)
        curses.init_pair(index, fg, bg)
        self.color_pairs[label] = {
            'index': index,
            'bg': bg,
            'fg': fg,
        }


    def color_attr(self, label):
        return curses.color_pair(self.color_pairs[label]['index'])


class TextComponent():
    DEFAULT_COLOR = 0


    def __init__(self, text, color=None):
        self.text = text
        self.color = color
        self._children = []


    @staticmethod
    def empty():
        return TextComponent("")


    def append(self, child):
        if isinstance(child, TextComponent):
            self._children.append(child)
        else:
            self._children.append(TextComponent(child))


    @staticmethod
    def set_default_color(color):
        TextComponent.DEFAULT_COLOR = color


    def add_to_scr(self, scr, y, x, parents=None):
        if parents is None:
            parents = []
        else:
            parents = list(parents)
            parents.insert(0, self)

        height, width = scr.getmaxyx()
        if y >= height:
            return x
        displayed_len = min(width - x, len(self.text))
        if not displayed_len:
            return x
        displayed_text = str(self.text)[:displayed_len]

        displayed_color = TextComponent.DEFAULT_COLOR
        for node in parents:
            if node.color is not None:
                displayed_color = node.color
                break

        scr.addstr(y, x, displayed_text, displayed_color)
        x += displayed_len

        for child in self._children:
            x = child.add_to_scr(scr, y, x, parents=parents)

        return x


    def __len__(self):
        return len(str(self))


    def __str__(self):
        return str(self.text) + "".join([str(child) for child in self._children])


class TableFormatter():
    def __init__(self, headers, delimiter):
        self._cells = {}
        self._col_widths = {}
        self._num_rows = 0
        self._num_cols = 0
        self._delimiter = delimiter
        self.add_row(headers)
        # Dummy row for --- separator
        self.add_row([])


    def add_row(self, row):
        y = self._num_rows
        self._num_rows += 1

        self._num_cols = max(self._num_cols, len(row))

        for x, text in enumerate(row):
            cell = text if isinstance(text, TextComponent) else TextComponent(text)
            self._cells[(y, x)] = cell


    def show_table(self, scr, scr_y, scr_x):
        self._calc_col_widths()
        last_col = self._num_cols - 1
        for cell_y in range(self._num_rows):
            y = scr_y + cell_y
            x = scr_x

            if cell_y == 1:
                table_width = len(self._delimiter) * (self._num_cols - 1)
                for cell_x in range(self._num_cols):
                    table_width += self._col_widths.get(cell_x, 0)
                TextComponent('-' * table_width).add_to_scr(scr, y, x)

            for cell_x in range(self._num_cols):
                cell = self._cells.get((cell_y, cell_x), None)
                if cell is None:
                    cell = TextComponent.empty()
                cell.add_to_scr(scr, y, x)
                x += self._col_widths.get(cell_x, 0)

                if cell_x < last_col:
                    x = self._delimiter.add_to_scr(scr, y, x)


    def _calc_col_widths(self):
        self._col_widths = {}
        for (_, x), text in self._cells.items():
            self._col_widths[x] = max(len(text), self._col_widths.get(x, 0))


async def display_main(stdscr, host):
    display = ShardHealthMonitorDisplay(stdscr, host)
    await display.run()


def main(stdscr, host) -> None:
    try:
        return asyncio.run(display_main(stdscr, host))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('host', help="RabbitMQ address")
    args = arg_parser.parse_args()

    curses.wrapper(main, args.host)
