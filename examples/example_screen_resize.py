"""Example ctx.screen Resize program."""

import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from zen_tui.basewidget import ACTION_OK, ACTION_CANCEL
from zen_tui.widgets import Dialog, WButton, WDropDown, WLabel, WListBox
# from zen_tui.menu import WMenuBar, WMenuBox
from zen_tui.context import Context
from zen_tui.defs import Color


# Dialog on the screen
d = None


# This routine is called on screen resize
def screen_resize(s):
    global d
    # Widgets in dialog store absolute screen coordinates, so
    # we need to recreate it from scratch for new dimensions.
    d = create_dialog()
    screen_redraw(s)


# This routine is called to redraw screen
def screen_redraw(s, _allow_cursor=False):
    global d
    s.attr_color(Color.C_WHITE, Color.C_BLUE)
    s.cls()
    s.attr_reset()
    d.redraw()


def create_dialog():
    global d
    width, height = ctx.screen.screen_size()

    d = Dialog((width - 40) // 2, (height - 13) // 2, 40, 13)
    d.add(1, 1, WLabel("Label:"))
    d.add(1, 2, WListBox(16, 4, [f"choice{i}" for i in range(10)]))
    d.add(1, 7, WDropDown(10, ["Red", "Green", "Yellow"]))

    b = WButton(8, "OK")
    d.add(3, 10, b)
    b.finish_dialog = ACTION_OK

    b = WButton(8, "Cancel")
    d.add(20, 10, b)
    b.finish_dialog = ACTION_CANCEL

    return d


with Context() as ctx:
    d = create_dialog()

    screen_redraw(ctx.screen)
    ctx.screen.set_screen_redraw(screen_redraw)
    ctx.screen.set_screen_resize(screen_resize)

    res = d.loop()


print("Result:", res)
