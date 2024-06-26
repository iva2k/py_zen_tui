"""Example Menu program."""

from zen_tui.menu import WMenuBar, WMenuBox
from zen_tui.widgets import ACTION_OK, ACTION_CANCEL, Dialog, WLabel, WButton, WListBox, WDropDown
from zen_tui.context import Context
from zen_tui.defs import Color, Keys


# Dialog on the screen
d = None

# This routine is called to redraw screen "in menu's background"
def screen_redraw(s, _allow_cursor=False):
    """Redraw screen in menu's background."""
    s.attr_color(Color.C_WHITE, Color.C_BLUE)
    s.cls()
    s.attr_reset()
    d.redraw()


# We have two independent widgets on screen: dialog and main menu,
# so can't call their individual loops, and instead should have
# "main loop" to route events to currently active widget, and
# switch the active one based on special events.
def main_loop(m):
    """Main Loop."""
    while 1:
        key = m.get_input()

        if isinstance(key, list):
            # Mouse click
            x, y = key
            if m.inside(x, y):
                m.focus = True

        if m.focus:
            # If menu is focused, it gets events. If menu is cancelled,
            # it loses focus. Otherwise, if menu selection is made, we
            # quit with with menu result.
            res = m.handle_input(key)
            if res == ACTION_CANCEL:
                m.focus = False
            elif res is not None and res is not True:
                return res
        else:
            # If menu isn't focused, it can be focused by pressing F9.
            if key == Keys.KEY_F9:
                m.focus = True
                m.redraw()
                continue
            # Otherwise, dialog gets input
            res = d.handle_input(key)
            if res is not None and res is not True:
                return res

def main():
    with Context() as ctx:
        global d
        d = Dialog(10, 5, 40, 14)
        d.add(12, 1, WLabel("Press F9 for menu"))
        d.add(1, 2, WLabel("Label:"))
        d.add(1, 3, WListBox(16, 4, [f"choice{i}" for i in range(10)]))
        d.add(1, 8, WDropDown(10, ["Red", "Green", "Yellow"]))

        b = WButton(8, "OK")
        d.add(10, 11, b)
        b.finish_dialog = ACTION_OK

        b = WButton(8, "Cancel")
        d.add(23, 11, b)
        b.finish_dialog = ACTION_CANCEL

        screen_redraw(ctx.screen)
        ctx.screen.set_screen_redraw(screen_redraw)

        menu_file = WMenuBox([("Open...", "Open"), ("Save", "S"), ("Save as...", "Sa"), ("Exit", "ex")])
        menu_edit = WMenuBox([("Copy", "copy"), ("Paste", "paste")])
        m = WMenuBar([("File", menu_file), ("Edit", menu_edit), ("About", "About")])
        m.permanent = True
        m.redraw()

        res = main_loop(m)


    print("Result:", res)

main()
