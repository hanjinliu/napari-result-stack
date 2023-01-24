import sys

from qtpy.QtGui import QFont


def monospace() -> str:
    if sys.platform == "win32":
        _font = "Consolas"
    elif sys.platform == "darwin":
        _font = "Menlo"
    else:
        _font = "Monospace"
    return _font


def monospace_font():
    return QFont(monospace())
