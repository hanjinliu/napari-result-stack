from __future__ import annotations

from magicgui.widgets import ComboBox
from qtpy import QtGui
from qtpy import QtWidgets as QtW
from qtpy.QtCore import Qt

from napari_result_stack._qt_const import monospace_font
from napari_result_stack.types import StoredMeta


class QResultViewer(QtW.QWidget):
    _current_instance: QResultViewer | None = None

    def __init__(self, parent: QtW.QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()
        self._widget = None
        # self._combobox.reset_choices()
        if (stored := self._combobox.value) is not None:
            self._on_combobox_changed(stored)

        self.__class__._current_instance = self

    @classmethod
    def current(cls) -> QResultViewer | None:
        """Get the current widget instance."""
        return cls._current_instance

    def update_choices(self):
        """Update the choices of the combo box."""
        # NOTE: Name of this method should not be reset_choices! Otherwise
        # this will be call every time layer is updated.
        self._combobox.reset_choices()

    def setWidget(self, wdt: QtW.QWidget):
        """Set the widget to be shown below the combo box."""
        if self._widget is not None:
            self._layout.removeWidget(self._widget)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.addWidget(wdt)
        self._widget = wdt

    def _on_combobox_changed(self, stored: StoredMeta):
        self.setWidget(stored.get_widget())

    def _setup_ui(self):
        _layout = self._layout = QtW.QVBoxLayout()
        _layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(_layout)

        self._combobox = ComboBox(choices=StoredMeta._get_choices_for_combobox)
        self._combobox.native.setFont(monospace_font())
        self._stack_widget = QtW.QStackedWidget()
        _layout.addWidget(self._combobox.native)
        self._combobox.changed.connect(self._on_combobox_changed)

        # header
        _label = QtW.QLabel("Type:")
        width = QtGui.QFontMetrics(_label.font()).width("Type:") + 8
        _label.setFixedWidth(width)
        _header = QtW.QWidget()

        _header_layout = QtW.QHBoxLayout()
        _header_layout.setContentsMargins(0, 0, 0, 0)
        _header_layout.addWidget(_label)
        _header_layout.addWidget(self._combobox.native)

        _header.setLayout(_header_layout)

        _layout.addWidget(_header)
