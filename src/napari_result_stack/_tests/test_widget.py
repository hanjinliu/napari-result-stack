from magicgui import magicgui
from pytestqt.qtbot import QtBot

from napari_result_stack import QResultViewer
from napari_result_stack.types import StoredMeta


def test_launch_widget(qtbot: QtBot):
    wdt = QResultViewer()
    qtbot.addWidget(wdt)


def test_add_type(qtbot: QtBot, stored: StoredMeta):
    wdt = QResultViewer()
    qtbot.addWidget(wdt)

    assert wdt._widget is None

    @magicgui
    def f(x: int) -> stored[int]:
        return x

    @magicgui
    def g(x: int) -> stored[int, 0]:
        return x

    assert wdt._widget.count() == 0
    f(0)
    assert wdt._widget.count() == 1
    g(0)
    assert wdt._widget.count() == 1
