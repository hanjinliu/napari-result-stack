from __future__ import annotations

from typing import Any, Callable, Iterator, MutableMapping, TypeVar, overload

from qtpy import QtGui
from qtpy import QtWidgets as QtW

from napari_result_stack._qt_const import monospace

_T = TypeVar("_T")
_WidgetFactory = Callable[[_T], QtW.QWidget]


class WidgetFactoryMap(MutableMapping[type, _WidgetFactory]):
    def __init__(self) -> None:
        self._map: dict[type, _WidgetFactory] = {}

    def __getitem__(self, __key: type) -> _WidgetFactory:
        return self._map[__key]

    def __setitem__(self, __key: type, __value: _WidgetFactory) -> None:
        if not isinstance(__value, Callable):
            raise TypeError("Widget factory must be a callable")
        self._map[__key] = __value

    def __delitem__(self, __key: type) -> None:
        del self._map[__key]

    def __iter__(self) -> Iterator[type]:
        return iter(self._map)

    def __len__(self) -> int:
        return len(self._map)

    def create_widget(self, val: Any) -> QtW.QWidget:
        """Create a widget for the given value."""
        typ = type(val)
        if factory := self.get(typ, None):
            return factory(val)
        for registered_type, factory in self.items():
            if issubclass(typ, registered_type):
                return factory(val)
        return self.default_factory(val)

    @overload
    def register(
        self, typ: type[_T]
    ) -> Callable[[_WidgetFactory[_T]], _WidgetFactory[_T]]:
        ...

    @overload
    def register(self, func: _WidgetFactory[_T]) -> _WidgetFactory[_T]:
        ...

    @overload
    def register(
        self, typ: type[_T], func: _WidgetFactory[_T]
    ) -> _WidgetFactory[_T]:
        ...

    def register(self, *args) -> _WidgetFactory:
        nargs = len(args)
        if nargs == 0:
            raise TypeError("register() requires at least one argument")
        if nargs == 1:
            arg = args[0]
            if type(arg) == type:
                return lambda func: self.register(arg, func)
            elif callable(arg):
                annot = arg.__annotations__
                if not isinstance(annot, dict):
                    raise TypeError(
                        "Factory function must have annotations if no type "
                        "is given."
                    )
                for k, v in annot.items():
                    if k != "returns":
                        typ = v
                        break
                else:
                    raise TypeError(
                        "Factory function must have an annotation for the "
                        "first argument if no type is given."
                    )
                return self.register(typ, arg)
        elif nargs == 2:
            typ, func = args
            if not callable(func):
                raise TypeError("Factory function must be a callable")
            self[typ] = func
            return func
        else:
            raise TypeError("register() takes at most 2 arguments")

    @staticmethod
    def default_factory(
        val: Any, converter: Callable[[Any], str] = repr
    ) -> QtW.QLabel:
        w = QtW.QLabel()
        text = converter(val)
        font = QtGui.QFont(monospace(), w.font().pointSize())
        w.setFont(font)
        if len(text) < 60:
            w.setText(text)
        else:
            w.setText(text[:56] + " ...")
        w.setToolTip(f"{text}\n({type(val).__name__})")
        return w


_GLOBAL_WIDGET_FACTORIES = WidgetFactoryMap()


def get_factories() -> WidgetFactoryMap:
    """Get the widget factory map object."""
    return _GLOBAL_WIDGET_FACTORIES
