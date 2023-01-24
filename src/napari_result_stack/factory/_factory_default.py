from __future__ import annotations

import datetime
import inspect
from enum import Enum
from pathlib import Path
from types import FunctionType
from typing import TYPE_CHECKING, Mapping

from ._factory import WidgetFactoryMap

if TYPE_CHECKING:
    pass


def _enum_repr(x: Enum):
    return f"{type(x).__name__}.{x.name}"


def _path_repr(x: Path):
    return str(x).replace("\\", "/")


def register_factories(wfactory: WidgetFactoryMap) -> None:
    import numpy as np
    import pandas as pd

    from ._dict_view import QDictView
    from ._table_view import QDataFrameView
    from ._text_view import QTextView

    _default = WidgetFactoryMap.default_factory

    wfactory.register(int, _default)
    wfactory.register(bool, _default)
    wfactory.register(float, _default)
    wfactory.register(str, _default)
    wfactory.register(Enum, lambda x: _default(x, _enum_repr))
    wfactory.register(Path, lambda x: _default(x, _path_repr))
    wfactory.register(datetime.datetime, lambda x: _default(x, str))
    wfactory.register(datetime.time, lambda x: _default(x, str))
    wfactory.register(datetime.date, lambda x: _default(x, str))
    wfactory.register(datetime.timedelta, lambda x: _default(x, str))
    wfactory.register(pd.DataFrame, QDataFrameView)
    wfactory.register(pd.Series, lambda x: QDictView(x.to_dict()))
    wfactory.register(Mapping, QDictView)
    wfactory.register(np.ndarray, lambda x: QTextView(repr(x)))
    wfactory.register(FunctionType, lambda x: QTextView(inspect.getsource(x)))
