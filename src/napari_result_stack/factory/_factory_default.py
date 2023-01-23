from __future__ import annotations

from typing import TYPE_CHECKING

from ._factory import WidgetFactoryMap

if TYPE_CHECKING:
    import pandas as pd


def table_factory(val: pd.DataFrame):
    from magicgui.widgets import Table

    # from ._table_view import QDataFrameView
    # return QDataFrameView(val)
    table = Table(value=val)
    return table.native


def register_factories(wfactory: WidgetFactoryMap) -> None:
    import pandas as pd

    wfactory.register(int, WidgetFactoryMap.default_factory)
    wfactory.register(bool, WidgetFactoryMap.default_factory)
    wfactory.register(float, WidgetFactoryMap.default_factory)
    wfactory.register(str, WidgetFactoryMap.default_factory)
    wfactory.register(pd.DataFrame, table_factory)
