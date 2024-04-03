"""Unit tests for zen_tui.widgets.WListBox"""

import unittest
from zen_tui.widgets import WListBox
from zen_tui.defs import Keys
from zen_tui.context import Context


class User:
    """ User class."""
    def __init__(self, name, age):
        self.name = name
        self.age = age


class UserListBox(WListBox):
    """ UserListBox class."""
    def __init__(self, width, height, items):
        super().__init__(w=width, h=height, items=items)

    def render_line(self, user: User) -> str:
        return user.name


class WListBoxTest(unittest.TestCase):
    """ WListBoxTest class."""
    def test_handle_key_with_custom_type_of_items(self):
        """Test handle_key() with custom type of items."""
        with Context():
            users = [User('admin', 30), User('root', 27)]
            widget = UserListBox(width=5, height=5, items=users)
            self.assertIsNone(widget.handle_key(Keys.KEY_DOWN))
