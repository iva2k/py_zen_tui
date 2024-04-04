"""Screen module."""

from __future__ import annotations

import os
import re
import signal
import sys

if os.name == "nt":
    import msvcrt
else:
    import fcntl
    import select
    import struct
    import termios
    import tty


class Screen:
    """Represents screen on ANSI terminal with stdin and stdout.

    It is a base class for Widget, therefore all Widgets inherit the Screen functionality.
    """
    def __init__(self) -> None:
        self._screen_width = 0
        self._screen_height = 0

    def wr(self, s: bytes | str) -> None:
        """Write string to screen."""
        if isinstance(s, str):
            s = bytes(s, "utf-8")
        # os.write(1, s)  # Doesn't print unicode bytes on Windows.
        sys.stdout.buffer.write(s)
        sys.stdout.buffer.flush()

    def wr_fixedw(self, s, width: int) -> None:
        """Write string in a fixed-width field."""
        s = s[:width]
        self.wr(s)
        self.wr(" " * (width - len(s)))
        # Doesn't work here, as it doesn't advance cursor
        # self.clear_num_pos(width - len(s))

    def cls(self) -> None:
        self.wr(b"\x1b[2J")

    def goto(self, x: int, y: int) -> None:
        # TODO: When Python is 3.5, update this to use bytes
        self.wr(f"\x1b[{y + 1};{x + 1}H")

    def clear_to_eol(self) -> None:
        self.wr(b"\x1b[0K")

    # Clear specified number of positions
    def clear_num_pos(self, num: int) -> None:
        if num > 0:
            self.wr(f"\x1b[{num}X")

    def attr_color(self, fg: int, bg: int = -1) -> None:
        max_color = 8
        fg_color_base = 30
        bg_color_base = 40
        if bg == -1:
            bg = fg >> 4
            fg &= 0xF
        if bg is None:
            if fg > max_color:
                self.wr(f"\x1b[{fg_color_base + fg - max_color};1m")
            else:
                self.wr(f"\x1b[{fg_color_base + fg}m")
        else:
            if bg > max_color:
                raise ValueError(f"Expected bg <= {max_color}")
            if fg > max_color:
                self.wr(f"\x1b[{fg_color_base + fg - max_color};{bg_color_base + bg};1m")
            else:
                self.wr(f"\x1b[0;{fg_color_base + fg};{bg_color_base + bg}m")


    def attr_reset(self) -> None:
        self.wr(b"\x1b[0m")

    def cursor(self, on: bool) -> None:
        if on:
            self.wr(b"\x1b[?25h")
        else:
            self.wr(b"\x1b[?25l")

    def draw_box(self, left: int, top: int, width: int, height: int) -> None:
        """Draw a box on the screen.
        
        Use http://www.utf8-chartable.de/unicode-utf8-table.pl for utf-8 pseudographic reference
        """
        ul = b"\xe2\x94\x8c"  # "┌"
        hr = b"\xe2\x94\x80"  # "─"
        ur = b"\xe2\x94\x90"  # "┐"
        bl = b"\xe2\x94\x94"  # "└"
        br = b"\xe2\x94\x98"  # "┘"
        vr = b"\xe2\x94\x82"  # "│"

        bottom = top + height - 1
        hor = hr * (width - 2)

        self.goto(left, top)
        self.wr(ul + hor + ur)
        self.goto(left, bottom)
        self.wr(bl + hor + br)

        top += 1
        while top < bottom:
            self.goto(left, top)
            self.wr(vr)
            self.goto(left + width - 1, top)
            self.wr(vr)
            top += 1

    def clear_box(self, left: int, top: int, width: int, height: int) -> None:
        # doesn't work
        #self.wr("\x1b[%s;%s;%s;%s$z" % (top + 1, left + 1, top + height, left + width))
        s = b" " * width
        bottom = top + height
        while top < bottom:
            self.goto(left, top)
            self.wr(s)
            top += 1

    def dialog_box(self, left: int, top: int, width: int, height: int, title="") -> None:
        self.clear_box(left + 1, top + 1, width - 2, height - 2)
        self.draw_box(left, top, width, height)
        if title:
            #pos = (width - len(title)) / 2
            pos = 1
            self.goto(left + pos, top)
            self.wr(title)

    def init_tty(self) -> None:
        if os.name == "nt":
            pass
        else:
            self.org_termios = termios.tcgetattr(0)
            tty.setraw(0)
        # TODO: (now) Figure out how to use it: self.screen_size(force_read=True)


    def deinit_tty(self) -> None:
        if os.name == "nt":
            pass
        elif self.org_termios:
            termios.tcsetattr(0, termios.TCSANOW, self.org_termios)

    def enable_mouse(self) -> None:
        # Mouse reporting - X10 compatibility mode
        # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking
        self.wr(b"\x1b[?1000h")  # SET_VT200_MOUSE
        # For "X10 compatibility mode" should be SET_X10_MOUSE 9:
        # self.wr(b"\x1b[?9h")  # SET_X10_MOUSE
        #? "\x1b[?1003h\x1b[?1015h\x1b[?1006h"

    def disable_mouse(self) -> None:
        # Mouse reporting - X10 compatibility mode
        self.wr(b"\x1b[?1000l")
        #? "\x1b[?1003l\x1b[?1015l\x1b[?1006l"
        # self.wr(b"\x1b[?9l")  # SET_X10_MOUSE - CLR

    def screen_size(self, force_read: bool = True) -> tuple[int, int]:
        if force_read or not self._screen_width or not self._screen_height:
            self._screen_width, self._screen_height = os.get_terminal_size()
            # if os.name == "nt":
            #     self.wr(b"\x1b[18t")
            #     resp = msvcrt.getch()
            #     assert resp.startswith(b"\x1b[8;") and resp[-1:] == b"t"
            #     vals = resp[:-1].split(b";")
            #     self._screen_width, self._screen_height = int(vals[2]), int(vals[1])
            # else:
            #     # From GNU source of stty(1)
            #     pad = "0" * 8
            #     s = fcntl.ioctl(1, termios.TIOCGWINSZ, pad)
            #     sz = struct.unpack('hhhh', s)
            #     rows, columns, _xpixels, _ypixels = sz
            #     # print("rows: {} columns: {}, xpixels: {}, ypixels: {}". format(*sz))
            #     self._screen_width, self._screen_height = int(columns), int(rows)

            #     # self.wr(b"\x1b[18t")
            #     ## import select
            #     #res = select.select([0], [], [], 0.2)[0]
            #     # if not res:
            #     #     return (80, 24)
            #     # resp = os.read(0, 32)
        return (self._screen_width, self._screen_height)

    # Set function to redraw an entire (client) screen
    # This is called to restore original screen, as we don't save it.
    def set_screen_redraw(self, handler) -> None:
        self.screen_redraw = handler

    def set_screen_resize(self, handler) -> None:
        if sig := getattr(signal, 'SIGWINCH', None):
            signal.signal(sig, lambda sig, stk: handler(self))

    def get_cursor_pos(self) -> tuple[int, int]:
        self.wr("\x1b[6n")
        if os.name == "nt":
            res = True
        else:
            # import select
            res = select.select([0], [], [], 0.2)[0]
            if not res:
                return -1, -1
        # if os.name == "nt":
        #     resp = msvcrt.getch()
        # else:
        #     resp = os.read(0, 32)
        # assert resp.startswith(b"\x1b[8;") and resp[-1:] == b"t"
        # vals = resp[:-1].split(b";")
        # return (int(vals[2]), int(vals[1]))

        data = b""
        while not data.endswith(b"R"):
            if os.name == "nt":
                data = data + msvcrt.getch()
            else:
                data = data + os.read(0, 32)
        # response data = "^[[{y};{x}R"
        res = re.match(r".*\[(?P<y>\d*);*(?P<x>\d*)R", data.decode())
        if not res:
            return -1, -1
        x = int(res.group("x")) - 1
        y = int(res.group("y")) - 1
        return x, y
