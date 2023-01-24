from __future__ import annotations

from magicgui.widgets import ComboBox
from qtpy import QtWidgets as QtW
from qtpy.QtCore import Qt

from napari_result_stack.types import _StoredMeta


class QResultInspector(QtW.QWidget):
    def __init__(self, parent: QtW.QWidget | None = None):
        super().__init__(parent)
        _layout = QtW.QVBoxLayout()
        _layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(_layout)

        self._combobox = ComboBox(
            choices=_StoredMeta._get_choices_for_combobox
        )
        _layout.addWidget(self._combobox.native)
        self._combobox.changed.connect(self._on_combobox_changed)

        self._layout = _layout
        self._widget = None
        self._combobox.reset_choices()
        if (stored := self._combobox.value) is not None:
            self._on_combobox_changed(stored)

    def setWidget(self, wdt: QtW.QWidget):
        if self._widget is not None:
            self._layout.removeWidget(self._widget)
        self._layout.addWidget(wdt)
        self._widget = wdt

    def _on_combobox_changed(self, stored: _StoredMeta):
        self.setWidget(stored.get_widget())
