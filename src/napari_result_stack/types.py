from __future__ import annotations

import typing
import weakref
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Hashable,
    TypeVar,
    overload,
)

from magicgui.widgets import ComboBox, LineEdit, Widget
from typing_extensions import Annotated, get_args, get_origin

if TYPE_CHECKING:
    from magicgui.widgets import FunctionGui
    from qtpy.QtWidgets import QComboBox

    from napari_result_stack.widgets import QResultStack


_T = TypeVar("_T")
_U = TypeVar("_U")


class DisplayLabel(LineEdit):
    """Widget to display the last stored value."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ann = self.annotation
        if isinstance(ann, _StoredMeta):
            widgets = _StoredMeta._bound_widgets[ann._hash_key()]
            if self not in widgets:
                widgets.append(self)
        self.enabled = False

    def reset_choices(self, *_):
        """Strictly is not reset 'choices' but for simplicity use this name."""
        self.value = repr(self.value)


class StoredValueComboBox(ComboBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from ._models import QComboBoxModel
        from ._qt_const import monospace_font

        qcombobox: QComboBox = self.native
        qcombobox.setFont(monospace_font())
        qcombobox.setModel(QComboBoxModel(qcombobox))
        qcombobox.view().setMinimumWidth(200)
        ann = self.annotation
        if isinstance(ann, _StoredMeta):
            self._default_choices = Stored._get_choice
        self.reset_choices()

    def reset_choices(self, *_: Any):
        super().reset_choices(*_)
        qcombobox: QComboBox = self.native
        if qcombobox.count() > 0:
            qcombobox.setCurrentIndex(qcombobox.count() - 1)


class _StoredLastAlias(type):
    @overload
    def __getitem__(cls, value: type[_T]) -> type[_T]:
        ...

    @overload
    def __getitem__(cls, value: tuple[type[_T], Hashable]) -> type[_T]:
        ...

    def __getitem__(cls, value):
        stored_cls = Stored._class_getitem(value)

        def _getter(w=None):
            store = stored_cls._store
            if len(store) > 0:
                return store[-1].value
            raise IndexError(f"Storage of {stored_cls} is empty.")

        return Annotated[
            stored_cls,
            {"bind": _getter, "widget_type": DisplayLabel, "visible": True},
        ]


class _StoredLast(Generic[_T], metaclass=_StoredLastAlias):
    def __new__(cls, *args, **kwargs):
        raise TypeError("Type StoredLast cannot be instantiated.")

    def __init_subclass__(cls, *args, **kwargs):
        raise TypeError(f"Cannot subclass {cls.__module__}.StoredLast.")


class _StoredMeta(type, Generic[_T]):
    _instances: dict[Hashable, _StoredMeta] = {}
    _bound_widgets: defaultdict[Hashable, list[Widget]] = defaultdict(list)

    _store: list[StoredValue[_T]]
    _count: int
    _maxsize: int
    _widget_ref: weakref.ReferenceType[QResultStack]
    _hash_value: Hashable
    __args__: tuple[type]

    @overload
    def __getitem__(cls, value: type[_U]) -> type[_U]:
        ...

    @overload
    def __getitem__(cls, value: tuple[type[_U], Hashable]) -> type[_U]:
        ...

    def __getitem__(cls, value):
        return Stored._class_getitem(value)

    def __repr__(cls: _StoredMeta) -> str:
        return cls.__name__

    def length(self) -> int:
        """The number of the storage."""
        return len(self._store)

    def clear(cls):
        """Clear the storage."""
        return cls._store.clear()

    def pop(cls, index: int = -1) -> StoredValue[_T]:
        """Pop the item at given index from the storage."""
        return cls._store.pop(index)

    def append(cls, value: _T):
        """Append the value to the storage."""
        widget = cls._widget()
        input_value = StoredValue(cls._count, value)
        cls._store.append(input_value)
        if widget is not None:
            widget.on_variable_added(input_value.label, input_value.value)
        cls._count += 1
        if len(cls._store) > cls._maxsize:
            cls._store.pop(0)
            if widget is not None:
                widget.on_overflown()

        # reset all the related categorical widgets.
        for w in _StoredMeta._bound_widgets.get(cls._hash_key(), []):
            w.reset_choices()
        return None

    def value(cls, index: int = -1) -> _T:
        """Get the value at given index from the storage."""
        return cls._store[index].value

    def get_widget(cls) -> QResultStack:
        """Get the widget for this storage type. Create if not exists."""
        if (listview := cls._widget()) is None:
            listview = cls._create_widget()
        return listview

    def _hash_key(cls) -> tuple[type[_T], Hashable]:
        return cls.__args__[0], cls._hash_value

    def _widget(self) -> QResultStack | None:
        """Return the widget for this storage type if exists."""
        if self._widget_ref is None:
            return None
        return self._widget_ref()

    def _create_widget(cls):
        from napari_result_stack.widgets import QResultStack

        listview = QResultStack(cls)
        for val in cls._store:
            listview.on_variable_added(val.label, val.value)
        cls._widget_ref = weakref.ref(listview)
        return listview

    @classmethod
    def _get_choices_for_combobox(cls, *_):
        return [(repr(stored), stored) for stored in cls._instances.values()]


_U = TypeVar("_U")


class DefaultSpec:
    def __repr__(self) -> str:
        return "<default>"

    def __hash__(self) -> int:
        return id(self)


class Stored(Generic[_T], metaclass=_StoredMeta):
    """
    Use variable store of specific type.

    ``Stored[T]`` is identical to ``T`` for the type checker. However, outputs
    are stored for later use in functions with the same annotation.
    """

    _count: int
    _maxsize: int
    _hash_value: Hashable
    _widget_ref: weakref.ReferenceType[QResultStack]
    Last = _StoredLast
    _no_spec = DefaultSpec()

    __args__: tuple[type] = ()
    _repr_map: dict[type[_U], Callable[[_U], str]] = {}

    @classmethod
    def new(cls, tp: type[_U], maxsize: int | None = None) -> Stored[_U]:
        """Create a new storage with given maximum size."""
        i = 0
        while (tp, i) in _StoredMeta._instances:
            i += 1
        outtype = Stored[tp, 0]
        if maxsize is None:
            maxsize = _maxsize_for_type(tp)
        else:
            if not isinstance(maxsize, int) or maxsize <= 0:
                raise TypeError("maxsize must be a positive integer")
            outtype._maxsize = maxsize
        return outtype

    @overload
    @classmethod
    def register_repr(
        cls, tp: type[_U], func: Callable[[_U], str]
    ) -> Callable[[_U], str]:
        ...

    @overload
    @classmethod
    def register_repr(
        cls, tp: type[_U]
    ) -> Callable[[Callable[[_U], str]], Callable[[_U], str]]:
        ...

    @classmethod
    def register_repr(cls, tp, func=None):
        """Register a function to convert a value to string."""

        def wrapper(f):
            if not callable(f):
                raise TypeError("func must be a callable")
            cls._repr_map[tp] = f
            return f

        return wrapper(func) if func is not None else wrapper

    @classmethod
    def _get_choice(cls, w: Widget):
        # NOTE: cls is Stored, not Stored[X]!
        ann: _StoredMeta = w.annotation
        widgets = _StoredMeta._bound_widgets[ann._hash_key()]
        if w not in widgets:
            widgets.append(w)
        return [(st.fmt(), st.value) for st in ann._store]

    @staticmethod
    def _store_value(gui: FunctionGui, value: _T, cls: _StoredMeta[_T]):
        cls.append(value)

        # Callback of the inner type annotation
        try:
            from magicgui.type_map import type2callback
        except ImportError:
            # magicgui < 0.7.0
            from magicgui.type_map import _type2callback as type2callback

        inner_type = cls.__args__[0]
        for cb in type2callback(inner_type):
            cb(gui, value, inner_type)

    @classmethod
    def _class_getitem(
        cls, value: type[_T] | tuple[type[_T], Hashable]
    ) -> _StoredMeta[_T]:
        if cls.__args__:
            raise TypeError("Cannot chain indexing.")
        if isinstance(value, tuple):
            if len(value) != 2:
                raise TypeError(
                    "Input of Stored must be a type or (type, Any)"
                )
            _tp, _hash = value
        else:
            if not _is_type_like(value):
                raise TypeError(
                    "The first argument of Stored must be a type but "
                    f"got {type(value)}."
                )
            _tp, _hash = value, cls._no_spec
        key: tuple[type[_T], Hashable] = (_tp, _hash)
        if outtype := _StoredMeta._instances.get(key):
            return outtype

        # NOTE: this string will be the class name.
        if _hash is cls._no_spec:
            name = f"Stored[{_type_name(_tp)}]"
        else:
            name = f"Stored[{_type_name(_tp)}, {_hash!r}]"

        ns = {
            "_store": [],
            "_count": 0,
            "_hash_value": _hash,
            "_maxsize": _maxsize_for_type(_tp),
            "_widget_ref": None,
        }
        outtype: cls = _StoredMeta(name, (cls,), ns)
        outtype.__args__ = (_tp,)
        _StoredMeta._instances[key] = outtype
        from napari_result_stack import QResultViewer

        if cur := QResultViewer.current():
            cur.update_choices()
        return outtype


def _is_type_like(x: Any):
    _tp = (type, typing._GenericAlias)  # noqa
    return isinstance(x, _tp) or hasattr(x, "__subclasshook__")


def _maxsize_for_type(tp: type[_T]) -> int:
    if hasattr(tp, "__array__"):
        return 12
    else:
        return 60


def _type_name(tp) -> str:
    if origin := get_origin(tp):
        origin_name = _type_name(origin)
        args = ", ".join(map(_type_name, get_args(tp)))
        return f"{origin_name}[{args}]"
    elif hasattr(tp, "__name__"):
        return tp.__name__
    elif hasattr(tp, "_name"):
        return tp._name
    elif tp in (..., None, NotImplemented):
        return str(tp)
    else:
        raise TypeError(f"Cannot get type name for {tp}")


class StoredValue(Generic[_T]):
    def __init__(self, label: Any, value: _T) -> None:
        self.label = label
        self.value = value

    def fmt(self) -> str:
        typ = type(self.value).__name__
        return f"({self.label}) {typ}\n{_repr_like(self.value)}"


def _repr_like(x: Any):
    lines = repr(x).split("\n")
    if len(lines) > 6:
        lines = lines[:6] + [" ... "]
    return "\n".join(lines)
