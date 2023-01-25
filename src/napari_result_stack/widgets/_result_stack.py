from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qtpy import QtWidgets as QtW
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    from napari_result_stack.types import _StoredMeta


class QResultStack(QtW.QWidget):
    def __init__(
        self,
        stored: _StoredMeta,
        parent: QtW.QWidget | None = None,
    ) -> None:
        from napari_result_stack.factory import (
            get_factories,
            register_factories,
        )

        super().__init__(parent)
        self._origin_stored_type = stored
        self._factories = get_factories()
        register_factories(self._factories)
        self._setup_scroll_area()

    def _setup_scroll_area(self) -> None:
        _layout = QtW.QVBoxLayout()
        _layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(0)
        self.setLayout(_layout)
        self._scroll_area = QtW.QScrollArea(self)
        self._scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll_area.setMinimumHeight(250)
        _layout.addWidget(self._scroll_area)
        self._scroll_area.setWidgetResizable(True)

        self._inner_widget = QtW.QWidget(self._scroll_area)
        self._scroll_area.setWidget(self._inner_widget)
        _inner_layout = QtW.QVBoxLayout()
        _inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        _inner_layout.setContentsMargins(2, 2, 2, 2)
        _inner_layout.setSpacing(1)
        self._inner_widget.setLayout(_inner_layout)
        self._inner_layout = _inner_layout
        return None

    def on_variable_added(self, label: Any, val: Any) -> None:
        qwidget = self._factories.create_widget(val)
        frame = QResultStackItem(str(label), qwidget, type(val), self)
        self._inner_layout.addWidget(frame)
        return None

    def on_variable_popped(self, index: int) -> None:
        if index < 0:
            index += self._inner_layout.count()
        self._inner_layout.removeWidget(
            self._inner_layout.itemAt(index).widget()
        )
        return None

    def widget(self, index: int) -> QtW.QWidget:
        """Return the widget at the given index"""
        return self._inner_layout.itemAt(index).widget()

    def count(self) -> int:
        """Return the number of items in the list"""
        return self._inner_layout.count()


class QResultStackItem(QtW.QGroupBox):
    def __init__(
        self, label: str, widget: QtW.QWidget, typ: type, parent: QResultStack
    ):
        super().__init__(parent)
        if isinstance(widget, QtW.QLabel):
            # simple types
            _layout = QtW.QHBoxLayout()
        else:
            _layout = QtW.QVBoxLayout()
        self.setLayout(_layout)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(2)

        # setup label
        _s = "&nbsp;"

        label = f"{_s}({label}){_s * 2}"
        label_text = (
            f"{_styled(label, 'gray', 'Arial')}{_styled(typ.__name__, 'lime')}"
        )

        self._label = _label_widget(label_text, self)
        font = self._label.font()
        font.setBold(True)
        self._label.setFont(font)
        self._label.setFixedWidth(90)
        self._label.setToolTip(f"{typ.__module__}.{typ.__name__}")

        _layout.addWidget(self._label)
        _layout.addWidget(widget)

        self.setMaximumHeight(max(widget.minimumHeight() + 16, 120))


def _label_widget(text: str, parent: QtW.QWidget) -> QtW.QLabel:
    wdt = QtW.QLabel(text, parent)
    wdt.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    wdt.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    wdt.setSizePolicy(
        QtW.QSizePolicy.Policy.Expanding, QtW.QSizePolicy.Policy.Expanding
    )
    return wdt


def _styled(text: str, color: str, family="monospace"):
    return f"<font color={color!r} family={family!r}>{text}</font>"
