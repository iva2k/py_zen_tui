"""BaseWidget module."""

from __future__ import annotations

import os

if os.name == "nt":
    import msvcrt

from .screen import Screen
from .defs import Keys


# Standard widget result actions (as return from .loop())
ACTION_OK = 1000
ACTION_CANCEL = 1001
ACTION_NEXT = 1002
ACTION_PREV = 1003

class Widget(Screen):
    """Widget class."""

    popup_class = None

    def __init__(self):
        self.multikeys: list[bytes] = [k for k in Keys.KEYMAP if isinstance(k, bytes) and len(k) > 1]

        self.signals = {}
        self.owner = None

        self.key_story = b""
        self.kbuf = b""
        self.top_line = 0
        self.cur_line = 0
        self.row = 0
        # self.col = 0
        self.x = 0
        self.y = 0
        self.height = 1  # height
        self.width = 80  # width
        self.margin = 0
        # self.t = ""
        self.h = 1
        self.w = 32
        self.focus = False
        self.col = 0  # len(text)
        self.just_started = True
        self.finish_dialog = False

    def reset(self) -> None:
        self.key_story = b""
        self.kbuf = b""
        self.top_line = 0
        self.cur_line = 0
        self.row = 0
        # self.col = 0
        self.x = 0
        self.y = 0
        self.height = 1  # height
        self.width = 80  # width
        self.margin = 0
        # self.t = ""
        self.h = 1
        self.w = 32
        self.focus = False
        # self.set(text)
        self.col = 0  # len(text)
        # self.adjust_cursor_eol()
        self.just_started = True
        self.finish_dialog = False
        # self.content: list[str] = [""]

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def inside(self, x, y):
        return self.y <= y < self.y + self.h and self.x <= x < self.x + self.w

    def signal(self, sig):
        if sig in self.signals:
            self.signals[sig](self)

    def on(self, sig, handler):
        self.signals[sig] = handler

    @staticmethod
    def longest(items):
        if not items:
            return 0
        return max((len(t) for t in items))

    def set_cursor(self):
        # By default, a widget doesn't use text cursor, so disables it
        self.cursor(onoff=False)

    def redraw(self) -> None:
        # raise NotImplementedError("Implement redraw()")
        pass


    def handle_mouse(self, _col: int, _row: int) -> bool:
        # raise NotImplementedError("Implement handle_mouse()")
        return False

    def handle_key(self, _key) -> bool | int | None:
        # raise NotImplementedError("Implement handle_key()")
        return False

    def get_choices(self, _substr: str, _only_prefix: bool=False):
        # raise NotImplementedError("Implement get_choices()")
        return []


    def get_chrs(self) -> bytes:
        if self.kbuf:
            # key = self.kbuf[0:1]
            # self.kbuf = self.kbuf[1:]
            key = self.kbuf
            self.kbuf = b""
        elif os.name == "nt":
            key = msvcrt.getch()
        else:
            key = os.read(0, 32)
        return key

    def maybe_multikey(self, key) -> tuple[int, bool]:
        """Determine if can map, or need to read another byte to map a multikey sequence.

        Args:
            key: One or more bytes of keys input.

        Returns:
            can_map, need_more: count of key bytes that can be mapped, and whether more bytes are needed.
        """
        if key.startswith(Keys.MOUSE_PREFIX):
            need_len = 6
            return need_len if len(key) >= need_len else 0, len(key) < need_len
        if Keys.MOUSE_PREFIX.startswith(key) and len(key) < len(Keys.MOUSE_PREFIX):
            return 0, True

        # return any(multikey.startswith(key) and len(key) < len(multikey) for multikey in self.multikeys)
        for multikey in Keys.KEYMAP:
            if key == multikey:
                return len(multikey), False  # No more bytes needed, can map
            if multikey.startswith(key) and len(key) < len(multikey):
                return 0, True  # More bytes needed to map
        return 0, False

    def get_input(self) -> bytes | int | list[int] | None:
        key = self.get_chrs()
        # length_multi = 0
        while True:
            can_map, need_more = self.maybe_multikey(key)
            if not need_more:
                break
            # length_multi = len(key)
            key = key + self.get_chrs()

        self.key_story = self.key_story + key

        if can_map:
            if key.startswith(Keys.MOUSE_PREFIX) and len(key) == Keys.MOUSE_LEN:
                # Decode mouse input (X10 compatibility mode SET_X10_MOUSE, Normal tracking mode SET_VT200_MOUSE, MOUSE_VT200_BUTTON1=):
                if key[3] not in [Keys.MOUSE_X10_BUTTON1, Keys.MOUSE_VT200_BUTTON1]:
                    return None
                row = key[5] - 33
                col = key[4] - 33
                return [col, row]
            key = Keys.KEYMAP.get(key, key)
        else:
            # Put the remainder of the key into the buffer
            key = key.decode()
            self.kbuf = key[1:].encode()
            key = key[0:1].encode()

        return key

    def handle_input(self, inp):
        if isinstance(inp, list):
            res = self.handle_mouse(inp[0], inp[1])
        else:
            res = self.handle_key(inp)
        return res


    def loop(self) -> bool | int:
        self.redraw()
        while True:
            key = self.get_input()
            if key is None:
                continue
            res = self.handle_input(key)

            if res is not None and res is not True:
            #? if res is not None:
                return res


class FocusableWidget(Widget):
    """FocusableWidget Widget class."""

    # If set to non-False, pressing Enter on this widget finishes
    # dialog, with Dialog.loop() return value being this value.
    finish_dialog = False


class EditableWidget(FocusableWidget):
    """EditableWidget Widget class."""

    def get(self):
        raise NotImplementedError


class ChoiceWidget(EditableWidget):
    """ChoiceWidget Widget class."""

    def __init__(self, choice):
        super().__init__()
        self.choice = choice

    def get(self):
        return self.choice


# Widget with few internal selectable items
class ItemSelWidget(ChoiceWidget):
    """ItemSelWidget Widget class."""

    def __init__(self, items):
        super().__init__(0)
        self.items = items

    def move_sel(self, direction):
        self.choice = (self.choice + direction) % len(self.items)
        self.redraw()
        self.signal("changed")
