"""
A demonstration on how to create QAbstractTableModel used in QTableView

The TableModel and ListModel are similar in many ways, one of the main
difference being the introduction of column; with that, the data model becomes
two-dimensional so the internal instance variable which is the representation
of the data self._colors is now a two-dimensional list instead of one-dimensional
(The nested list for colors won't make sense in terms of the context
but only serve as a demonstration).

The table model also doesn't need parent argument
as it isn't a hierarchical model

official documents: https://doc.qt.io/qt-5/qabstracttablemodel.html
subclassing: https://doc.qt.io/qt-5/qabstracttablemodel.html#subclassing
"""

import sys

from Qt import QtGui, QtCore, QtWidgets


class PaletteTableModel(QtCore.QAbstractTableModel):
    def __init__(self, colors, headers, parent=None):
        """
        Override: initialization

        :param colors: list. nested list of QColors
        :param headers: list. header names
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._colors = colors
        self._headers = headers

    def rowCount(self, parent):
        return len(self._colors)

    def columnCount(self, parent):
        """
        Override: number of columns (of the given parent).
        """
        return len(self._colors[0])

    def flags(self, index):
        return (QtCore.Qt.ItemIsEditable |
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable)

    def data(self, index, role):
        row_index = index.row()
        column_index = index.column()
        color = self._colors[row_index][column_index]

        if role == QtCore.Qt.EditRole:
            return color.name()

        if role == QtCore.Qt.ToolTipRole:
            return "Hex code: {}".format(color.name())

        if role == QtCore.Qt.DecorationRole:
            pixmap = QtGui.QPixmap(26, 26)
            pixmap.fill(color)
            icon = QtGui.QIcon(pixmap)
            return icon

        if role == QtCore.Qt.DisplayRole:
            return color.name()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row_index = index.row()
        column_index = index.column()
        color = self._colors[row_index][column_index]
        
        if role == QtCore.Qt.EditRole:
            if color.isValid():
                self._colors[row][column] = color
                self.dataChanged.emit(index, index)
                return True

        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section < len(self._headers):
                    return self._headers[section]
                else:
                    return "not implemented"
            else:
                return "Color {}".format(section)

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position+rows-1)
        for i in range(rows):
            default = [
                QtGui.QColor("#000000")
                for _ in range(self.columnCount(None))
            ]
            self._colors.insert(position, default)
        self.endInsertRows()
        return True

    def insertColumns(self, position, columns, parent=QtCore.QModelIndex()):
        """
        Override: insert number of new columns into the model at the given
        column position under certain parent.

        :param position: int. starting column position to insert
        :param columns: int. number of columns to insert
        :param parent: QModelIndex. index of the parent
        :return: bool. whether or not operation succeeded
        """
        self.beginInsertColumns(parent, position, position+columns-1)
        rows = self.rowCount(None)
        for _ in range(columns):
            for row_index in range(rows):
                self._colors[row_index].insert(
                    position,
                    QtGui.QColor("#000000")
                )
        self.endInsertColumns()
        return True


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # the input data needs to be two-dimensional
    rowCount = 4
    columnCount = 6
    data = [
        [QtGui.QColor("#FFFF00") for column in range(columnCount)]
        for row in range(rowCount)
    ]

    color_headers = [
        "Palette",
        "Colors",
        "Brushes",
        "Omg"
        "Technical",
        "Artist"
    ]
    model = PaletteTableModel(data, color_headers)
    model.insertColumns(0, 5)

    tableView = QtWidgets.QTableView()
    tableView.setModel(model)
    tableView.show()

    sys.exit(app.exec_())
