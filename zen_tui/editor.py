"""Editor Widget."""

from __future__ import annotations
#
# Simple VT100 terminal text editor widget
# Copyright (c) 2015-2020 Paul Sokolovsky
# Distributed under MIT License
#
import sys

from .basewidget import Widget
from .defs import Keys


class Editor(Widget):
    """Editor Widget class."""
    def __init__(self, x=0, y=0, width=80, height=24):
        Widget.__init__(self)
        self.top_line = 0
        self.cur_line = 0
        self.row = 0
        self.col = 0
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.margin = 0
        self.content: list[str] = []
        self.total_lines = 0

    def set_cursor(self):
        self.goto(self.col + self.x, self.row + self.y)
        self.cursor(on=True)

    def adjust_cursor_eol(self):
        # Returns True if entire window needs redraw
        val = 0
        if self.content:
            val = self.col + self.margin
            if val > 0:
                # Note: adjust_cursor_eol() may be called from widgets
                # where self.content is not guaranteed to be a str.
                val = min(val, len(self.content[self.cur_line]))
        if val > self.width - 1:
            self.margin = val - (self.width - 1)
            self.col = self.width - 1
            return True
        else:
            self.col = val - self.margin
            return False

    def set_lines(self, lines: list[str]) -> None:
        self.content = lines
        self.total_lines = len(lines)

    def redraw(self) -> None:
        self.cursor(on=False)
        i = self.top_line
        for c in range(self.height):
            self.goto(self.x, self.y + c)
            if i >= self.total_lines:
                self.show_line("", -1)
            else:
                self.show_line(self.content[i], i)
                i += 1
        self.set_cursor()

    def update_line(self):
        self.cursor(on=False)
        self.goto(self.x, self.row + self.y)
        self.show_line(self.content[self.cur_line], self.cur_line)
        self.set_cursor()

    def show_line(self, line: str, _i: int):
        line = line[self.margin:]
        line = line[:self.width]
        self.wr(line)
        self.clear_num_pos(self.width - len(line))

    def next_line(self):
        if self.row + 1 == self.height:
            self.top_line += 1
            return True
        else:
            self.row += 1
            return False

    def handle_cursor_keys(self, key) -> bool:
        if not self.total_lines:
            return False
        if key == Keys.KEY_DOWN:
            if self.cur_line + 1 != self.total_lines:
                self.cur_line += 1
                redraw = self.adjust_cursor_eol()
                if self.next_line() or redraw:
                    self.redraw()
                else:
                    self.set_cursor()
        elif key == Keys.KEY_UP:
            if self.cur_line > 0:
                self.cur_line -= 1
                redraw = self.adjust_cursor_eol()
                if self.row == 0:
                    if self.top_line > 0:
                        self.top_line -= 1
                        self.redraw()
                else:
                    self.row -= 1
                    if redraw:
                        self.redraw()
                    else:
                        self.set_cursor()
        elif key == Keys.KEY_LEFT:
            if self.col > 0:
                self.col -= 1
                self.set_cursor()
            elif self.margin > 0:
                self.margin -= 1
                self.redraw()
        elif key == Keys.KEY_RIGHT:
            self.col += 1
            if self.adjust_cursor_eol():
                self.redraw()
            else:
                self.set_cursor()
        elif key == Keys.KEY_HOME:
            self.col = 0
            if self.margin > 0:
                self.margin = 0
                self.redraw()
            else:
                self.set_cursor()
        elif key == Keys.KEY_END:
            self.col = len(self.content[self.cur_line])
            if self.adjust_cursor_eol():
                self.redraw()
            else:
                self.set_cursor()
        elif key == Keys.KEY_PGUP:
            self.cur_line -= self.height
            self.top_line -= self.height
            if self.top_line < 0:
                self.top_line = 0
                self.cur_line = 0
                self.row = 0
            elif self.cur_line < 0:
                self.cur_line = 0
                self.row = 0
            self.adjust_cursor_eol()
            self.redraw()
        elif key == Keys.KEY_PGDN:
            self.cur_line += self.height
            self.top_line += self.height
            if self.cur_line >= self.total_lines:
                self.top_line = self.total_lines - self.height
                self.cur_line = self.total_lines - 1
                if self.top_line >= 0:
                    self.row = self.height - 1
                else:
                    self.top_line = 0
                    self.row = self.cur_line
            self.adjust_cursor_eol()
            self.redraw()
        else:
            return False
        return True

    def handle_mouse(self, col: int, row: int) -> bool:
        row -= self.y
        col -= self.x
        if 0 <= row < self.height and 0 <= col < self.width:
            cur_line = self.top_line + row
            if cur_line < self.total_lines:
                self.row = row
                self.col = col
                self.cur_line = cur_line
                self.adjust_cursor_eol()
                self.set_cursor()
                return True
        return False

    def handle_key(self, key) -> bool | int | None:
        if key == Keys.KEY_QUIT:
            return key
        if self.handle_cursor_keys(key):
            return None
        return self.handle_edit_key(key)

    def handle_edit_key(self, key) -> bool | None:
        line = self.content[self.cur_line]
        if key == Keys.KEY_ENTER:
            self.content[self.cur_line] = line[:self.col + self.margin]
            self.cur_line += 1
            self.content[self.cur_line:self.cur_line] = [line[self.col + self.margin:]]
            self.total_lines += 1
            self.col = 0
            self.margin = 0
            self.next_line()
            self.redraw()
        elif key == Keys.KEY_BACKSPACE:
            if self.col + self.margin:
                if self.col:
                    self.col -= 1
                else:
                    self.margin -= 1
                line = line[:self.col + self.margin] + line[self.col + self.margin + 1:]
                self.content[self.cur_line] = line
                self.update_line()
        elif key == Keys.KEY_DELETE:
            line = line[:self.col + self.margin] + line[self.col + self.margin + 1:]
            self.content[self.cur_line] = line
            self.update_line()
        else:
            line = line[:self.col + self.margin] + str(key, "utf-8") + line[self.col + self.margin:]
            self.content[self.cur_line] = line
            self.col += 1
            self.adjust_cursor_eol()
            self.update_line()
        return None

    def deinit_tty(self):
        # Don't leave cursor in the middle of screen
        self.goto(0, self.height)
        super().deinit_tty()


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        content = f.read().splitlines()
        #content = f.readlines()


#os.write(1, b"\x1b[18t")
#key = os.read(0, 32)
#print(repr(key))

#key = os.read(0, 32)
#print(repr(key))

    e = Editor()
    e.init_tty()
    e.enable_mouse()
    e.set_lines(content)
    e.loop()
    e.deinit_tty()
