"""Context Manager module."""

from collections.abc import Mapping

from .screen import Screen


class Context:
    """Context Manager class, a singleton."""
    def __new__(cls, *args, **kwargs):
        it_id = "__it__"
        # getattr will dip into base classes, so __dict__ must be used
        it = cls.__dict__.get(it_id, None)
        if it is not None:
            return it
        # it = object.__new__(cls)
        it = super(Context, cls).__new__(cls)
        setattr(cls, it_id, it)
        it.init(*args, **kwargs)
        return it

    def init(self, *args: object, **kwargs: Mapping[str, object]) -> None:
        # Instance initialization
        self.clear_screen = kwargs.get("clear_screen", True)
        self.use_mouse = kwargs.get("use_mouse", True)
        self.screen = Screen()

    def __enter__(self):
        self.screen.init_tty()
        if self.use_mouse:
            self.screen.enable_mouse()
        if self.clear_screen:
            self.screen.cls()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.use_mouse:
            self.screen.disable_mouse()
        self.screen.goto(0, self.screen._screen_height or 50)
        self.screen.cursor(on=True)
        self.screen.deinit_tty()
        # This makes sure that entire screenful is scrolled up, and
        # any further output happens on a normal terminal line.
        print()
