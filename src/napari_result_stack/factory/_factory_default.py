from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

from ._factory import WidgetFactoryMap

if TYPE_CHECKING:
    import pandas as pd


def table_factory(val: pd.DataFrame):
    from ._table_view import QDataFrameView

    return QDataFrameView(val)


def series_factory(val: pd.Series):
    from ._dict_view import QDictView

    return QDictView(val.to_dict())


def dict_factory(val: dict):
    from ._dict_view import QDictView

    return QDictView(val)


def register_factories(wfactory: WidgetFactoryMap) -> None:
    import pandas as pd

    wfactory.register(int, WidgetFactoryMap.default_factory)
    wfactory.register(bool, WidgetFactoryMap.default_factory)
    wfactory.register(float, WidgetFactoryMap.default_factory)
    wfactory.register(str, WidgetFactoryMap.default_factory)
    wfactory.register(pd.DataFrame, table_factory)
    wfactory.register(pd.Series, series_factory)
    wfactory.register(Mapping, dict_factory)
