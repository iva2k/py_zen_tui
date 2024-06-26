"""This example shows a way to "serialize" results of a preference-style dialog."""

import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from pprint import pprint

from zen_tui.context import Context
from zen_tui.basewidget import EditableWidget
from zen_tui.widgets import ACTION_OK, ACTION_CANCEL, Dialog, WButton, WCheckbox, WComboBox, WFrame, WLabel, WListBox, WDropDown, WAutoComplete, WMultiEntry, WRadioButton, WTextEntry
from zen_tui.defs import Color


with Context() as ctx:
    ctx.screen.attr_color(Color.C_WHITE, Color.C_BLUE)
    ctx.screen.cls()
    ctx.screen.attr_reset()

    d = Dialog(5, 5, 50, 12)

    # Can add a raw string to dialog, will be converted to WLabel
    d.add(1, 1, "Label:")
    d.add(11, 1, WLabel("it's me!"))

    d.add(1, 2, "Entry:")
    w = WTextEntry(4, "foo")
    w.tag = "entry"
    d.add(11, 2, w)

    d.add(1, 3, "Dropdown:")
    w = WDropDown(10, ["Red", "Green", "Yellow"])
    w.tag = "dropdown"
    d.add(11, 3, w)

    d.add(1, 4, "Combo:")
    w = WComboBox(8, "fo", ["foo", "foobar", "bar"])
    w.tag = "combo"
    d.add(11, 4, w)

    d.add(1, 5, "Auto complete:")
    w = WAutoComplete(8, "fo", ["foo", "foobar", "bar", "car", "dar"])
    w.tag = "autocomp"
    d.add(15, 5, w)

    d.add(1, 8, "Multiline:")
    w = WMultiEntry(26, 3, ["Example", "Text"])
    w.tag = "multiline"
    d.add(1, 9, w)

    d.add(30, 1, WFrame(18, 6, "Frame"))
    w = WCheckbox("State")
    w.tag = "checkbox"
    d.add(31, 2, w)
    w = WRadioButton(["Red", "Green", "Yellow"])
    w.tag = "radio"
    d.add(31, 3, w)

    d.add(30, 8, "List:")
    w = WListBox(16, 4, [f"choice{i}" for i in range(10)])
    w.tag = "list"
    d.add(30, 9, w)

    b = WButton(8, "OK")
    d.add(10, 16, b)
    b.finish_dialog = ACTION_OK

    b = WButton(8, "Cancel")
    d.add(30, 16, b)
    b.finish_dialog = ACTION_CANCEL

    res = d.loop()


print()
print("Result:", res)

data = {}
for w in d.childs:
    if isinstance(w, EditableWidget):
        val = w.get()
        if val is not None:
            data[w.tag] = val

pprint(data)
