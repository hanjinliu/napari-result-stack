import pandas as pd
import pytest
from magicgui import magicgui
from pytestqt.qtbot import QtBot
from qtpy.QtWidgets import QComboBox

from napari_result_stack import QResultViewer
from napari_result_stack.types import StoredMeta


def test_launch_widget(qtbot: QtBot):
    wdt = QResultViewer()
    qtbot.addWidget(wdt)


def test_create_widget(stored: StoredMeta):
    stored.valuesof[int].append(0)
    st: StoredMeta = stored[int]
    st.get_widget()


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


def test_add_and_create(qtbot: QtBot, stored: StoredMeta):
    @magicgui
    def f(x: int) -> stored[int]:
        return x

    f(0)
    f(1)
    wdt = QResultViewer()
    qtbot.addWidget(wdt)

    assert wdt._widget.count() == 2


def test_close_button(qtbot: QtBot, stored: StoredMeta):
    wdt = QResultViewer()
    qtbot.addWidget(wdt)

    @magicgui
    def f(x: int) -> stored[int]:
        return x

    f(0)
    f(1)
    f(2)
    assert wdt._widget.count() == 3
    wdt._widget.widget(1)._close_button.click()
    assert wdt._widget.count() == 2
    assert stored.valuesof[int][0] == 0
    assert stored.valuesof[int][1] == 2


def test_popped(qtbot: QtBot, stored: StoredMeta):
    wdt = QResultViewer()
    qtbot.addWidget(wdt)

    @magicgui
    def f(x: int) -> stored[int]:
        return x

    f(0)
    f(1)
    f(2)
    assert wdt._widget.count() == 3
    stored.valuesof[int].pop(1)
    assert list(stored.valuesof[int]) == [0, 2]
    assert wdt._widget.count() == 2
    assert stored.valuesof[int][0] == 0
    assert stored.valuesof[int][1] == 2


def test_maxsize_changed(qtbot: QtBot, stored: StoredMeta):
    wdt = QResultViewer()
    qtbot.addWidget(wdt)

    @magicgui
    def f(x: int) -> stored[int]:
        return x

    f(0)
    f(1)
    f(2)
    assert wdt._widget.count() == 3
    stored.valuesof[int].maxsize = 2
    assert list(stored.valuesof[int]) == [1, 2]
    assert wdt._widget.count() == 2
    assert stored.valuesof[int][0] == 1
    assert stored.valuesof[int][1] == 2


def _func(x, y):
    """Some description."""
    out = x + y
    return out


class MyList(list):
    pass


@pytest.mark.parametrize(
    "value",
    [
        0,
        "a",
        {"a": 3, "b": [1, 2]},
        [1, 2],
        MyList([1, 2, 3]),
        pd.DataFrame(
            {"a": [1, 2], "b": [3e-5, 0.4], "c": [1e-3 + 1e-3j, 2.2 - 1j]}
        ),
        pd.Series([1, 2, 4]),
        _func,
    ],
)
def test_registered_types(value, qtbot: QtBot, stored: StoredMeta):
    wdt = QResultViewer()
    qtbot.addWidget(wdt)

    @magicgui
    def f() -> stored[object]:
        return value

    f()


def test_popup(qtbot: QtBot, stored: StoredMeta):
    wdt = QResultViewer()
    qtbot.addWidget(wdt)

    @magicgui
    def f(x: int) -> stored[int]:
        return x


def test_magicgui_construction(qtbot: QtBot, stored: StoredMeta):
    @magicgui
    def provide() -> stored[int]:
        return 0

    @magicgui
    def receive(x: stored[int]):
        return x + 1

    provide.show()
    receive.show()
    qtbot.addWidget(receive.native)
    provide()
    receive()
    cbox: QComboBox = receive.x.native
    cbox.showPopup()
