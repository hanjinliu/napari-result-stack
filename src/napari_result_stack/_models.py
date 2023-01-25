from __future__ import annotations

from qtpy import QtCore, QtGui
from qtpy.QtCore import Qt


class QComboBoxModel(QtGui.QStandardItemModel):
    """This model enables multi-line text for ComboBox."""

    def data(
        self,
        index: QtCore.QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role == Qt.ItemDataRole.SizeHintRole:
            text: str = self.data(index, Qt.ItemDataRole.DisplayRole)
            lines = text.split("\n")
            nline = len(lines)
            metric = QtGui.QFontMetrics(self.parent().font())
            width = max(metric.width(line) for line in lines)
            height = metric.height() * nline + 8
            return QtCore.QSize(width, height)
        return super().data(index, role)
