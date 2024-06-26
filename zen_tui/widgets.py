"""Dialog Widget."""

from __future__ import annotations

import sys

from .basewidget import ACTION_OK, ACTION_CANCEL, ACTION_NEXT, ACTION_PREV, ChoiceWidget, FocusableWidget, EditableWidget, ItemSelWidget, Widget
from .editorext import EditorExt
from .defs import Color, Keys, DOWN_ARROW


__all__ = (
    "ACTION_OK",
    "ACTION_CANCEL",
    "ACTION_NEXT",
    "ACTION_PREV",
    "EditableWidget",
    "Dialog",
    "WLabel",
    "WFrame",
    "WButton",
    "WCheckbox",
    "WRadioButton",
    "WListBox",
    "WPopupList",
    "WDropDown",
    "WTextEntry",
    "WPasswdEntry",
    "WMultiEntry",
    "WComboBox",
    "WCompletionList",
    "WAutoComplete",
)

class Dialog(Widget):
    """Dialog Widget class."""
    finish_on_esc = True

    def __init__(self, x: int, y: int, w: int=0, h: int=0, title=""):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = ""
        if title:
            self.title = f" {title} "
        self.childs = []
        # On both sides
        self.border_w = 2
        self.border_h = 2
        self.focus_w = None
        self.focus_idx = -1

    def add(self, x: int, y: int, widget: str | Widget):
        if isinstance(widget, str):
            # Convert raw string to WLabel
            widget = WLabel(widget)
        widget.set_xy(self.x + x, self.y + y)
        self.childs.append(widget)
        widget.owner = self

    def autosize(self, extra_w: int=0, extra_h: int=0):
        w = 0
        h = 0
        for wid in self.childs:
            w = max(w, wid.x - self.x + wid.w)
            h = max(h, wid.y - self.y + wid.h)
        self.w = max(self.w, w + self.border_w - 1) + extra_w
        self.h = max(self.h, h + self.border_h - 1) + extra_h

    def redraw(self) -> None:
        # Init some state on first redraw
        if self.focus_idx == -1:
            self.autosize()
            self.focus_idx, self.focus_w = self.find_focusable_by_idx(0, 1)
            if self.focus_w:
                self.focus_w.focus = True

        # Redraw widgets with cursor off
        self.cursor(on=False)
        self.dialog_box(self.x, self.y, self.w, self.h, self.title)
        for w in self.childs:
            w.redraw()
        # Then give widget in focus a chance to enable cursor
        if self.focus_w:
            self.focus_w.set_cursor()

    def find_focusable_by_idx(self, from_idx, direction):
        sz = len(self.childs)
        while 0 <= from_idx < sz:
            if isinstance(self.childs[from_idx], FocusableWidget):
                return from_idx, self.childs[from_idx]
            from_idx = (from_idx + direction) % sz
        return None, None

    def find_focusable_by_xy(self, x, y):
        i = 0
        for w in self.childs:
            if isinstance(w, FocusableWidget) and w.inside(x, y):
                return i, w
            i += 1
        return None, None

    def change_focus(self, widget):
        if widget is self.focus_w:
            return
        if self.focus_w:
            self.focus_w.focus = False
            self.focus_w.redraw()
        self.focus_w = widget
        widget.focus = True
        widget.redraw()
        widget.set_cursor()

    def move_focus(self, direction):
        prev_idx = (self.focus_idx + direction) % len(self.childs)
        self.focus_idx, new_w = self.find_focusable_by_idx(prev_idx, direction)
        self.change_focus(new_w)

    def handle_key(self, key) -> bool | int | None:
        if key == Keys.KEY_QUIT:
            return key
        if key == Keys.KEY_ESC and self.finish_on_esc:
            return ACTION_CANCEL
        if key == Keys.KEY_TAB:
            self.move_focus(1)
        elif key == Keys.KEY_SHIFT_TAB:
            self.move_focus(-1)
        elif self.focus_w:
            if key == Keys.KEY_ENTER:
                if self.focus_w.finish_dialog is not False:
                    return self.focus_w.finish_dialog
            res = self.focus_w.handle_key(key)
            if res == ACTION_PREV:
                self.move_focus(-1)
            elif res == ACTION_NEXT:
                self.move_focus(1)
            else:
                return res
        return None

    def handle_mouse(self, x, y):
        # Work in absolute coordinates
        if self.inside(x, y):
            self.focus_idx, w = self.find_focusable_by_xy(x, y)
#            print(w)
            if w:
                self.change_focus(w)
                return w.handle_mouse(x, y)


class WLabel(Widget):
    """WLabel Widget class."""

    def __init__(self, text, w=0):
        super().__init__()
        self.t = text
        self.h = 1
        self.w = w
        if not w:
            self.w = len(text)

    def redraw(self) -> None:
        self.goto(self.x, self.y)
        self.wr_fixedw(self.t, self.w)


class WFrame(Widget):
    """WFrame Widget class."""

    def __init__(self, w, h, title=""):
        super().__init__()
        self.w = w
        self.h = h
        self.t = title

    def redraw(self) -> None:
        self.draw_box(self.x, self.y, self.w, self.h)
        if self.t:
            pos = 1
            self.goto(self.x + pos, self.y)
            self.wr(f" {self.t} ")


class WButton(FocusableWidget):
    """WButton Widget class."""
    def __init__(self, w, text):
        super().__init__()
        self.t = text
        self.h = 1
        self.w = w or len(text) + 2
        self.disabled = False
        self.focus = False
        self.finish_dialog = False

    def redraw(self) -> None:
        self.goto(self.x, self.y)
        if self.disabled:
            self.attr_color(Color.C_WHITE, Color.C_GRAY)
        else:
            if self.focus:
                self.attr_color(Color.C_B_WHITE, Color.C_GREEN)
            else:
                self.attr_color(Color.C_BLACK, Color.C_GREEN)
        self.wr(self.t.center(self.w))
        self.attr_reset()

    def handle_mouse(self, _x, _y):
        if not self.disabled:
            if self.finish_dialog is not False:
                return self.finish_dialog
            else:
                self.signal("click")

    def handle_key(self, key) -> bool | int | None:
        if key == Keys.KEY_UP or key == Keys.KEY_LEFT:
            return ACTION_PREV
        if key == Keys.KEY_DOWN or key == Keys.KEY_RIGHT:
            return ACTION_NEXT
        # For dialog buttons (.finish_dialog=True), Keys.KEY_ENTER won't
        # reach here.
        if key == Keys.KEY_ENTER:
            self.signal("click")
        return None

    def on_click(self):
        pass


class WCheckbox(ChoiceWidget):
    """WCheckbox Widget class."""

    def __init__(self, title, choice=False):
        super().__init__(choice)
        self.t = title
        self.h = 1
        self.w = 4 + len(title)
        self.focus = False

    def redraw(self) -> None:
        self.goto(self.x, self.y)
        if self.focus:
            self.attr_color(Color.C_B_BLUE, None)
        self.wr("[x] " if self.choice else "[ ] ")
        self.wr(self.t)
        self.attr_reset()

    def flip(self):
        self.choice = not self.choice
        self.redraw()
        self.signal("changed")

    def handle_mouse(self, _x, _y):
        self.flip()

    def handle_key(self, key) -> bool | int | None:
        if key == Keys.KEY_UP:
            return ACTION_PREV
        if key == Keys.KEY_DOWN:
            return ACTION_NEXT
        if key == b" ":
            self.flip()
        return None


class WRadioButton(ItemSelWidget):
    """ WRadioButton Widget class."""

    def __init__(self, items):
        super().__init__(items)
        self.h = len(items)
        self.w = 4 + self.longest(items)
        self.focus = False

    def redraw(self) -> None:
        i = 0
        if self.focus:
            self.attr_color(Color.C_B_BLUE, None)
        for t in self.items:
            self.goto(self.x, self.y + i)
            self.wr("(*) " if self.choice == i else "( ) ")
            self.wr(t)
            i += 1
        self.attr_reset()

    def handle_mouse(self, _x, y):
        self.choice = y - self.y
        self.redraw()
        self.signal("changed")

    def handle_key(self, key) -> bool | int | None:
        if key == Keys.KEY_UP:
            self.move_sel(-1)
        elif key == Keys.KEY_DOWN:
            self.move_sel(1)
        return None


class WListBox(EditorExt, ChoiceWidget):
    """ WListBox Widget class."""

    def __init__(self, w: int, h: int, items: list[str]):
        EditorExt.__init__(self)
        ChoiceWidget.__init__(self, 0)
        self.width = w
        self.w = w
        self.height = h
        self.h = h
        self.set_items(items)
        self.focus = False

    def set_items(self, items):
        self.items = items
        self.set_lines(items)

    def render_line(self, line) -> str:
        # Default identity implementation is suitable for
        # items being list of strings.
        return line

    def show_line(self, line: str, i: int) -> None:
        hlite = self.cur_line == i
        if hlite:
            if self.focus:
                self.attr_color(Color.C_B_WHITE, Color.C_GREEN)
            else:
                self.attr_color(Color.C_BLACK, Color.C_GREEN)
        if i != -1:
            line = self.render_line(line)[:self.width]
            self.wr(line)
        self.clear_num_pos(self.width - len(line))
        if hlite:
            self.attr_reset()

    def handle_mouse(self, x, y):
        res = super().handle_mouse(x, y)
        self.choice = self.cur_line
        self.redraw()
        self.signal("changed")
        return res

    def handle_key(self, key) -> bool | int | None:
        res = super().handle_key(key)
        self.choice = self.cur_line
        self.redraw()
        self.signal("changed")
        return res

    def handle_edit_key(self, key):
        pass

    def set_cursor(self) -> None:
        Widget.set_cursor(self)

    def cursor(self, on: bool) -> None:
        # Force off
        super().cursor(on=False)


class WPopupList(Dialog):
    """ WPopupList Widget class."""

    main_widget: EditableWidget | None = None
    class OneShotList(WListBox):
        """OneShotList Widget class."""

        def handle_key(self, key) -> bool | int | None:
            if key == Keys.KEY_ENTER:
                return ACTION_OK
            if key == Keys.KEY_ESC:
                return ACTION_CANCEL
            return super().handle_key(key)

        def handle_mouse(self, x, y) -> int:
            if super().handle_mouse(x, y) is True:
                # (Processed) mouse click finishes selection
                return ACTION_OK

    def __init__(self, x: int, y: int, w: int, h: int, items: list[str], sel_item: int=0) -> None:
        super().__init__(x, y, w, h)
        self.list = self.OneShotList(w - 2, h - 2, items)
        self.list.cur_line = sel_item
        self.add(1, 1, self.list)

    def handle_mouse(self, x, y):
        if not self.inside(x, y):
            return ACTION_CANCEL
        return super().handle_mouse(x, y)

    def get_choice(self):
        return self.list.cur_line

    def get_selected_value(self):
        if not self.list.content:
            return None
        return self.list.content[self.list.cur_line]


class WDropDown(ChoiceWidget):
    """WDropDown Widget class."""

    def __init__(self, w: int, items: list[str], *, dropdown_h: int=5) -> None:
        super().__init__(0)
        self.items = items
        self.h = 1
        self.w = w
        self.dropdown_h = dropdown_h
        self.focus = False

    def redraw(self) -> None:
        self.goto(self.x, self.y)
        if self.focus:
            self.attr_color(Color.C_B_WHITE, Color.C_CYAN)
        else:
            self.attr_color(Color.C_BLACK, Color.C_CYAN)
        self.wr_fixedw(self.items[self.choice], self.w - 1)
        self.attr_reset()
        self.wr(DOWN_ARROW)

    def handle_mouse(self, _x, _y):
        popup = WPopupList(self.x, self.y + 1, self.w, self.dropdown_h, self.items, self.choice)
        res = popup.loop()
        if res == ACTION_OK:
            self.choice = popup.get_choice()
            self.signal("changed")
        self.owner.redraw()

    def handle_key(self, _key) -> bool | int | None:
        self.handle_mouse(0, 0)
        return None


class WTextEntry(EditorExt, EditableWidget):
    """WTextEntry Widget class."""

    def __init__(self, w: int, text: str):
        super(EditorExt, self).__init__(self, width=w, height=1)
        # super(EditableWidget, self).__init__()
        self.t = text
        self.h = 1
        self.w = w
        self.focus = False
        self.set(text)
        self.col = len(text)
        self.adjust_cursor_eol()
        self.just_started = True

    def get(self):
        return self.get_cur_line()

    def set(self, text):
        self.set_lines([text])

    def handle_cursor_keys(self, key):
        if super().handle_cursor_keys(key):
            if self.just_started:
                self.just_started = False
                self.redraw()
            return True
        return False

    def handle_edit_key(self, key):
        if key == Keys.KEY_ENTER:
            # Don't treat as editing key
            return True
        if self.just_started:
            if key != Keys.KEY_BACKSPACE:
                # Overwrite initial string with new content
                self.set_lines([""])
                self.col = 0
            self.just_started = False

        return super().handle_edit_key(key)

    def handle_mouse(self, x, y):
        if self.just_started:
            self.just_started = False
            self.redraw()
        super().handle_mouse(x, y)

    def show_line(self, line: str, i):
        if self.just_started:
            fg = Color.C_WHITE
        else:
            fg = Color.C_BLACK
        self.attr_color(fg, Color.C_CYAN)
        super().show_line(line, i)
        self.attr_reset()


class WPasswdEntry(WTextEntry):
    """WPasswdEntry Widget class."""

    def show_line(self, line: str, i: int) -> None:
        super().show_line("*" * len(line), i)


class WMultiEntry(EditorExt, EditableWidget):
    """WMultiEntry Widget class."""

    def __init__(self, w: int, h: int, lines: list[str]):
        super(EditorExt, self).__init__(self, width=w, height=h)
        # super(EditableWidget, self).__init__()
        self.h = h
        self.w = w
        self.focus = False
        self.set_lines(lines)

    def get(self):
        return self.content

    def set(self, lines):
        self.set_lines(lines)

    def show_line(self, line, i):
        self.attr_color(Color.C_BLACK, Color.C_CYAN)
        super().show_line(line, i)
        self.attr_reset()


class WComboBox(WTextEntry):
    """WComboBox Widget class."""

    popup_class = WPopupList
    popup_h = 5

    def __init__(self, w, text, items):
        # w - 1 width goes to Editor widget
        super().__init__(w - 1, text)
        # We have full requested width, will show arrow symbol as last char
        self.w = w
        self.items = items

    def redraw(self) -> None:
        self.goto(self.x + self.w - 1, self.y)
        self.wr(DOWN_ARROW)
        super().redraw()

    def get_choices(self, _substr: str, _only_prefix: bool=False):
        return self.items

    def show_popup(self):
        choices = self.get_choices(self.get())
        popup = self.popup_class(self.x, self.y + 1, self.longest(choices) + 2, self.popup_h, choices)
        popup.main_widget = self
        res = popup.loop()
        if res == ACTION_OK:
            val = popup.get_selected_value()
            if val is not None:
                self.set_lines([val])
                self.margin = 0
                self.col = sys.maxsize
                self.adjust_cursor_eol()
                self.just_started = False
        self.owner.redraw()

    def handle_key(self, key) -> bool | int | None:
        if key == Keys.KEY_DOWN:
            self.show_popup()
        else:
            return super().handle_key(key)
        return None

    def handle_mouse(self, x, y):
        if x == self.x + self.w - 1:
            self.show_popup()
        else:
            super().handle_mouse(x, y)


class WCompletionList(WPopupList):
    """WCompletionList Widget class."""

    def __init__(self, x: int, y: int, w: int, h: int, items: list[str]):
        super().__init__(x, y, w, h, items=[])
        self.list = self.OneShotList(w - 2, h - 2, items)
        self.add(1, 1, self.list)
        chk = WCheckbox("Prefix")
        def is_prefix_changed(wid):
            main = self.main_widget
            choices = main.get_choices(main.get(), wid.choice) if main else []
            self.list.set_lines(choices)
            self.list.top_line = 0
            self.list.cur_line = 0
            self.list.row = 0
            self.list.redraw()
        chk.on("changed", is_prefix_changed)
        self.add(1, h - 1, chk)


class WAutoComplete(WComboBox):
    """WAutoComplete Widget class."""

    popup_class = WCompletionList

    def get_choices(self, substr: str, only_prefix: bool=False):
        substr = substr.lower()
        if only_prefix:
            choices = list(filter(lambda x: x.lower().startswith(substr), self.items))
        else:
            choices = list(filter(lambda x: substr in x.lower(), self.items))
        return choices
