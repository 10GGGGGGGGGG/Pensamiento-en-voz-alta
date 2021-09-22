from PyQt5 import QtCore


class PandasModel(QtCore.QAbstractTableModel):
    # Class to populate a table view with a pandas dataframe
    def __init__(self, data, header, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.header = header
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole and self.header:
            return self._data.columns[col]
        return QtCore.QAbstractTableModel.headerData(self, col, orientation, role)
