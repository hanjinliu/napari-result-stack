from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Mapping

from ._factory import WidgetFactoryMap

if TYPE_CHECKING:
    pass


def _enum_repr(x: Enum):
    return f"{type(x).__name__}.{x.name}"


def _path_repr(x: Path):
    return str(x).replace("\\", "/")


def register_factories(wfactory: WidgetFactoryMap) -> None:
    import pandas as pd

    from ._dict_view import QDictView
    from ._table_view import QDataFrameView

    wfactory.register(int, WidgetFactoryMap.default_factory)
    wfactory.register(bool, WidgetFactoryMap.default_factory)
    wfactory.register(float, WidgetFactoryMap.default_factory)
    wfactory.register(str, WidgetFactoryMap.default_factory)
    wfactory.register(
        Enum, lambda x: WidgetFactoryMap.default_factory(x, _enum_repr)
    )
    wfactory.register(
        Path, lambda x: WidgetFactoryMap.default_factory(x, _path_repr)
    )
    wfactory.register(pd.DataFrame, QDataFrameView)
    wfactory.register(pd.Series, lambda x: QDictView(x.to_dict()))
    wfactory.register(Mapping, QDictView)
