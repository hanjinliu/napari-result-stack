from __future__ import annotations

from qtpy import QtGui
from qtpy import QtWidgets as QtW

from napari_result_stack._qt_const import monospace


class QTextView(QtW.QTextEdit):
    def __init__(self, val: str):
        super().__init__()
        self.setReadOnly(True)
        self.setWordWrapMode(QtGui.QTextOption.WrapMode.NoWrap)
        self.setText(val)
        self.setFont(QtGui.QFont(monospace()))
        self.setMinimumHeight(120)
