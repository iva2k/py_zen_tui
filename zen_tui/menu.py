"""Menu Widgets."""

from __future__ import annotations

from .screen import Screen
from .basewidget import ACTION_CANCEL, ACTION_PREV, ACTION_NEXT, Widget, ItemSelWidget
from .defs import Color, Keys


class WMenuBar(ItemSelWidget):
    """Menu Bar Widget class."""

    def __init__(self, menu_struct) -> None:
        super().__init__(menu_struct)
        self.x = self.y = 0
        self.h = 1
        self.w = Screen.screen_size()[0]
        self.pulled_down = False
        self.focus = False
        self.permanent = False

    def redraw(self) -> None:
        if self.focus:
            self.cursor(onoff=False)
        self.goto(self.x, self.y)
        i = 0
        for name, _pulldown in self.items:
            if self.focus and i == self.choice:
                self.attr_color(Color.C_B_WHITE, Color.C_BLACK)
            self.wr(b"  ")
            self.wr(name)
            self.wr(b"  ")
            self.attr_reset()
            i += 1

    def close(self):
        """Close Menu."""
        self.focus = False
        self.screen_redraw(True)
        if self.permanent:
            self.redraw()

    def get_item_x(self, item_no: int) -> int:
        """Get Item X position."""
        x = self.x
        i = 0
        for name, _pulldown in self.items:
            if i == item_no:
                break
            x += len(name) + 4
            i += 1
        return x

    def handle_key(self, key) -> bool | int | None:
        # We need while to auto pull down submenus on left/right keys
        while True:
            res = None
            action = False
            sel = self.items[self.choice][1]
            if key == Keys.KEY_ESC:
                self.close()
                return ACTION_CANCEL
            elif key == Keys.KEY_LEFT:
                if self.pulled_down:
                    self.screen_redraw()
                self.move_sel(-1)
            elif key == Keys.KEY_RIGHT:
                if self.pulled_down:
                    self.screen_redraw()
                self.move_sel(1)
            elif key == Keys.KEY_ENTER:
                self.pulled_down = True
                action = True
            elif key == Keys.KEY_DOWN and isinstance(sel, Widget):
                self.pulled_down = True
            else:
                return None

            sel = self.items[self.choice][1]
            if isinstance(sel, Widget) and self.pulled_down:
                sel.set_xy(self.get_item_x(self.choice), self.y + 1)
                res = sel.loop()
                if res == ACTION_PREV:
                    key = Keys.KEY_LEFT
                    continue
                if res == ACTION_NEXT:
                    key = Keys.KEY_RIGHT
                    continue
                if res == ACTION_CANCEL:
                    self.pulled_down = False
                    self.screen_redraw()
                    self.redraw()
                    return None

                self.close()
                return res
            elif action:
                self.close()
                return sel

            # continue

    def handle_mouse(self, x, y):
        # Works in absolute coordinates
        if y != self.y:
            return
        x -= self.x
        cur_x = 0
        found = False
        i = 0
        for name, _pulldown in self.items:
            cur_x += len(name) + 4
            if x <= cur_x:
                found = True
                break
            i += 1
        if not found:
            return
        self.choice = i
        self.redraw()
        return self.handle_key(Keys.KEY_ENTER)


class WMenuBox(ItemSelWidget):
    """WMenuBox Widget class."""

    def __init__(self, items):
        super().__init__(items)
        self.x = self.y = 0
        self.h = len(items) + 2
        w = 0
        for i in items:
            w = max(w, len(i[0]))
        self.w = w + 2

    def redraw(self) -> None:
        self.dialog_box(self.x, self.y, self.w, self.h)
        i = 0
        for item in self.items:
            self.goto(self.x + 1, self.y + i + 1)
            if i == self.choice:
                self.attr_color(Color.C_B_WHITE, Color.C_BLACK)
            self.wr_fixedw(item[0], self.w - 2)
            self.attr_reset()
            i += 1

    def handle_key(self, key) -> bool | int | None:
        if key == Keys.KEY_ESC:
            return ACTION_CANCEL
        elif key == Keys.KEY_UP:
            self.move_sel(-1)
        elif key == Keys.KEY_DOWN:
            self.move_sel(1)
        elif key == Keys.KEY_LEFT:
            return ACTION_PREV
        elif key == Keys.KEY_RIGHT:
            return ACTION_NEXT
        elif key == Keys.KEY_ENTER:
            return self.items[self.choice][1]
        return None

    def handle_mouse(self, x, y):
        if not self.inside(x, y):
            return ACTION_CANCEL
        y -= self.y + 1
        if 0 <= y < self.h - 2:
            self.choice = y
            return self.items[self.choice][1]
