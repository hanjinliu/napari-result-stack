import sys


def monospace() -> str:
    if sys.platform == "win32":
        _font = "Consolas"
    elif sys.platform == "darwin":
        _font = "Menlo"
    else:
        _font = "Monospace"
    return _font
