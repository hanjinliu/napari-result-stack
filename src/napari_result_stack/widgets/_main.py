from __future__ import annotations

from magicgui.widgets import ComboBox
from qtpy import QtGui
from qtpy import QtWidgets as QtW
from qtpy.QtCore import Qt

from napari_result_stack._qt_const import monospace
from napari_result_stack.types import _StoredMeta


class QResultViewer(QtW.QWidget):
    _current_instance: QResultViewer | None = None

    def __init__(self, parent: QtW.QWidget | None = None):
        super().__init__(parent)
        _layout = QtW.QVBoxLayout()
        _layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(_layout)

        self._combobox = ComboBox(
            choices=_StoredMeta._get_choices_for_combobox
        )
        self._combobox.native.setFont(QtGui.QFont(monospace()))
        self._stack_widget = QtW.QStackedWidget()
        _layout.addWidget(self._combobox.native)
        self._combobox.changed.connect(self._on_combobox_changed)

        self._layout = _layout
        self._widget = None
        self._combobox.reset_choices()
        if (stored := self._combobox.value) is not None:
            self._on_combobox_changed(stored)

        self.__class__._current_instance = self

    @classmethod
    def current(cls) -> QResultViewer | None:
        return cls._current_instance

    def update_choices(self):
        # NOTE: Name of this method should not be reset_choices! Otherwise
        # this will be call every time layer is updated.
        self._combobox.reset_choices()

    def setWidget(self, wdt: QtW.QWidget):
        if self._widget is not None:
            self._layout.removeWidget(self._widget)
        self._layout.addWidget(wdt)
        self._widget = wdt

    def _on_combobox_changed(self, stored: _StoredMeta):
        self.setWidget(stored.get_widget())
