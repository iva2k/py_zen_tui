zen_tui
=======

zen_tui is a Text User Interface (TUI) widget library for Python3.
It is known to work with CPython3 and
`Pycopy <https://github.com/pfalcon/pycopy>`_ (Unix version is
officially supported for the latter), but should work with any
Python3 implementation which allows to access stdin/stdout file
descriptors.

It was forked from Picotui on 2024-0401 and heavily modified.

Screenshot:

.. image:: https://raw.githubusercontent.com/iva2k/py_zen_tui/master/zen_tui.png

Documentation
-------------

Zen_tui is an experimental WIP project, and the best documentation currently
is the source code (https://github.com/iva2k/py_zen_tui/tree/master/zen_tui)
and examples (see below).

Examples
--------

* example_widgets.py - Shows repertoire of widgets, inside a dialog.
* example_menu.py - Shows a "fullscreen" application with a main menu.
* example_dialogs.py - Shows some standard dialogs.
* examples/ - More assorted examples.

Known Issues
------------

Pay attention to what Unicode font you use in your console. Some Linux
distributions, e.g. Ubuntu, are known to have a broken Unicode font
installed by default, which causes various visual artifacts (specifically,
Ubuntu Mono font isn't really monospace - many Unicode pseudographic
characters have double (or so) width, box-drawing symbols have gaps, etc.)

Compare
-------

* https://github.com/shade40/Slate
