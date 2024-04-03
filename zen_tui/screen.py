"""Screen module."""

from __future__ import annotations

import os
import re
import signal
import sys

if os.name == "nt":
    import msvcrt
else:
    import select
    import termios
    import tty


class Screen:
    """Represents screen on ANSI terminal with stdin and stdout.

    It is a base class for Widget, therefore all Widgets inherit the Screen functionality.

    The design pattern here is special to the intended use:

    * All methods shoud be `@staticmethod` (attention to NOT use `self` or `cls`), so `Screen.XXX()` can be called statically when needed (e.g. by clients of this package).
    * All subclasses should call using self.XXX().
    * Any subclass can override any of the base methods, and use `self` argument.

    One downside to this design pattern is that it is hardcoded to use stdin and stdout, and cannot change that without a redesign.

    There is also a group of `@classmethod` methods, which are intended to be NOT overriden.

    """

    @staticmethod
    def wr(s: bytes | str) -> None:
        """Write string to screen."""
        if isinstance(s, str):
            s = bytes(s, "utf-8")
        # os.write(1, s)  # Doesn't print unicode bytes on Windows.
        sys.stdout.buffer.write(s)
        sys.stdout.buffer.flush()

    @staticmethod
    def wr_fixedw(s, width: int) -> None:
        """Write string in a fixed-width field."""
        s = s[:width]
        Screen.wr(s)
        Screen.wr(" " * (width - len(s)))
        # Doesn't work here, as it doesn't advance cursor
        # Screen.clear_num_pos(width - len(s))

    @staticmethod
    def cls() -> None:
        Screen.wr(b"\x1b[2J")

    @staticmethod
    def goto(x: int, y: int) -> None:
        # TODO: When Python is 3.5, update this to use bytes
        Screen.wr(f"\x1b[{y + 1};{x + 1}H")

    @staticmethod
    def clear_to_eol() -> None:
        Screen.wr(b"\x1b[0K")

    # Clear specified number of positions
    @staticmethod
    def clear_num_pos(num: int) -> None:
        if num > 0:
            Screen.wr(f"\x1b[{num}X")

    @staticmethod
    def attr_color(fg: int, bg: int = -1) -> None:
        max_color = 8
        fg_color_base = 30
        bg_color_base = 40
        if bg == -1:
            bg = fg >> 4
            fg &= 0xF
        if bg is None:
            if fg > max_color:
                Screen.wr(f"\x1b[{fg_color_base + fg - max_color};1m")
            else:
                Screen.wr(f"\x1b[{fg_color_base + fg}m")
        else:
            if bg > max_color:
                raise ValueError(f"Expected bg <= {max_color}")
            if fg > max_color:
                Screen.wr(f"\x1b[{fg_color_base + fg - max_color};{bg_color_base + bg};1m")
            else:
                Screen.wr(f"\x1b[0;{fg_color_base + fg};{bg_color_base + bg}m")


    @staticmethod
    def attr_reset() -> None:
        Screen.wr(b"\x1b[0m")

    @staticmethod
    def cursor(onoff: bool) -> None:
        if onoff:
            Screen.wr(b"\x1b[?25h")
        else:
            Screen.wr(b"\x1b[?25l")

    @staticmethod
    def draw_box(left: int, top: int, width: int, height: int) -> None:
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

        Screen.goto(left, top)
        Screen.wr(ul + hor + ur)
        Screen.goto(left, bottom)
        Screen.wr(bl + hor + br)

        top += 1
        while top < bottom:
            Screen.goto(left, top)
            Screen.wr(vr)
            Screen.goto(left + width - 1, top)
            Screen.wr(vr)
            top += 1

    @staticmethod
    def clear_box(left: int, top: int, width: int, height: int) -> None:
        # doesn't work
        #self.wr("\x1b[%s;%s;%s;%s$z" % (top + 1, left + 1, top + height, left + width))
        s = b" " * width
        bottom = top + height
        while top < bottom:
            Screen.goto(left, top)
            Screen.wr(s)
            top += 1

    def dialog_box(self, left: int, top: int, width: int, height: int, title="") -> None:
        self.clear_box(left + 1, top + 1, width - 2, height - 2)
        self.draw_box(left, top, width, height)
        if title:
            #pos = (width - len(title)) / 2
            pos = 1
            self.goto(left + pos, top)
            self.wr(title)

    @classmethod
    def init_tty(cls) -> None:
        if os.name == "nt":
            pass
        else:
            cls.org_termios = termios.tcgetattr(0)
            tty.setraw(0)

    @classmethod
    def deinit_tty(cls) -> None:
        if os.name == "nt":
            pass
        elif cls.org_termios:
            termios.tcsetattr(0, termios.TCSANOW, cls.org_termios)

    @classmethod
    def enable_mouse(cls) -> None:
        # Mouse reporting - X10 compatibility mode
        # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking
        cls.wr(b"\x1b[?1000h")  # SET_VT200_MOUSE
        # For "X10 compatibility mode" should be SET_X10_MOUSE 9:
        # cls.wr(b"\x1b[?9h")  # SET_X10_MOUSE
        #? "\x1b[?1003h\x1b[?1015h\x1b[?1006h"

    @classmethod
    def disable_mouse(cls) -> None:
        # Mouse reporting - X10 compatibility mode
        cls.wr(b"\x1b[?1000l")
        #? "\x1b[?1003l\x1b[?1015l\x1b[?1006l"
        # cls.wr(b"\x1b[?9l")  # SET_X10_MOUSE - CLR

    @classmethod
    def screen_size(cls) -> tuple[int, int]:
        cls.wr(b"\x1b[18t")
        if os.name == "nt":
            res = True
        else:
            # import select
            res = select.select([0], [], [], 0.2)[0]
        if not res:
            return (80, 24)
        if os.name == "nt":
            resp = msvcrt.getch()
        else:
            resp = os.read(0, 32)
        assert resp.startswith(b"\x1b[8;") and resp[-1:] == b"t"
        vals = resp[:-1].split(b";")
        return (int(vals[2]), int(vals[1]))

    # Set function to redraw an entire (client) screen
    # This is called to restore original screen, as we don't save it.
    @classmethod
    def set_screen_redraw(cls, handler) -> None:
        cls.screen_redraw = handler

    @classmethod
    def set_screen_resize(cls, handler) -> None:
        if sig := getattr(signal, 'SIGWINCH', None):
            signal.signal(sig, lambda sig, stk: handler(cls))

    @staticmethod
    def get_cursor_pos() -> tuple[int, int]:
        Screen.wr("\x1b[6n")
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
