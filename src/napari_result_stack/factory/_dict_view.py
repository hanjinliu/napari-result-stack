from __future__ import annotations

from qtpy import QtCore
from qtpy import QtWidgets as QtW
from qtpy.QtCore import Qt


class QDictModel(QtCore.QAbstractTableModel):
    """Table model for data frame."""

    def __init__(self, d: dict, parent=None):
        super().__init__(parent)
        self._dict = d
        self._keys = list(d.keys())

    def rowCount(self, parent=None):
        return len(self._dict)

    def columnCount(self, parent=None):
        return 1

    def data(
        self,
        index: QtCore.QModelIndex,
        role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole,
    ):
        if not index.isValid():
            return QtCore.QVariant()
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            r = index.row()
            key = self._keys[r]
            val = self._dict[key]
            return repr(val)
        return QtCore.QVariant()

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if orientation == Qt.Orientation.Vertical:
            if role == Qt.ItemDataRole.DisplayRole:
                if section >= len(self._dict):
                    return None
                return repr(self._keys[section])


class QDictView(QtW.QTableView):
    def __init__(self, d: dict) -> None:
        super().__init__()
        self.setModel(QDictModel(d))
        self.horizontalHeader().hide()
        self.resizeRowsToContents()
        self.horizontalHeader().resizeSection(0, 1000)
