"""
A demonstration on how to create QAbstractListModel used in QListView

official documentation: https://doc.qt.io/qt-5/qabstractlistmodel.html

Notes:
QVariant:
https://stackoverflow.com/questions/21217399/pyqt4-qtcore-qvariant-object-instead-of-a-string
For Python2, by default, PyQt will automatically convert a python object
to a QVariant when you set it, but it won't automatically convert them
back again when you retrieve it.

For Python3, by default, the conversion is always done automatically in
both directions, so the extra step is not needed.
"""


import sys

from Qt import QtGui, QtCore, QtWidgets


class PaletteListModel(QtCore.QAbstractListModel):
    def __init__(self, colors, parent=None):
        """
        Initialization

        :param colors: list. list of QColors
        :param parent: QModelIndex. list model doesn't need a parent since
        it isn't a hierarchical structure, thus default to null pointer
        """
        QtCore.QAbstractListModel.__init__(self, parent)
        self._colors = colors

    def headerData(self, section, orientation, role):
        """
        Override: header value of data in given role, section and orientation

        :param section: int. section number corresponding to column number
        a.k.a, which index of the header
        :param orientation: Qt.Orientation. horizontal or vertical header
        :param role: Qt.ItemDataRole. given role of the data
        :return: QVariant. data value of the given role, section, orientation
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return 'Palette'
            else:
                return 'Color {}'.format(section + 1)

    def rowCount(self, parent):
        """
        Override: number of rows of given parent. when the parent is valid
        rowCount returns the number of children of the parent, which is used
        in hierarchical structure like QTreeView

        :param parent: QModelIndex. index of the parent item
        :return: int. number of rows
        """
        return len(self._colors)

    def data(self, index, role):
        """
        Override: data stored under given role for item of index

        :param index: QModelIndex. index of the item
        :param role: Qt.ItemDataRole. given role of the data
        :return:
        """
        row = index.row()
        value = self._colors[row]

        if role == QtCore.Qt.EditRole:
            return value.name()

        if role == QtCore.Qt.ToolTipRole:
            return "Hex code: {}".format(value.name())

        if role == QtCore.Qt.DecorationRole:
            pixmap = QtGui.QPixmap(26, 26)
            pixmap.fill(value)
            icon = QtGui.QIcon(pixmap)
            return icon

        if role == QtCore.Qt.DisplayRole:
            return value.name()

    def flags(self, index):
        """
        Override: item flags of the given index

        :param index: QModelIndex. index of the item
        :return: Qt.ItemFlags. combination of flags describes properties of
        an item
        """
        return (QtCore.Qt.ItemIsEditable |
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable)

    def setData(self, index, value, role):
        """
        Override: sets the data value of given index of given role

        see also:
        when re-implementing the setData() function, this signal must
        be emitted explicitly
        https://doc.qt.io/qt-5/qabstractitemmodel.html#dataChanged

        :param index: QModelIndex. index of the item
        :param value: QVariant. data value of the given role, index
        :param role: Qt.ItemDataRole. given role of the data
        :return: bool. whether or not operation succeeded
        """
        if role == QtCore.Qt.EditRole:
            row = index.row()
            color = QtGui.QColor(value)
            if color.isValid():
                self._colors[row] = color

                # emit dataChanged signal to sync with display
                self.dataChanged.emit(index, index)
                return True

        return False

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        """
        Override: insert number of rows into the model before a given row
        under certain parent (making it the child of the parent), when
        in a hierarchical structure

        see also:
        https://doc.qt.io/qt-5/qabstractitemmodel.html#beginInsertRows

        :param position: int. starting row position to insert
        :param rows: int. number of rows to insert
        :param parent: QModelIndex. index of the parent
        :return: bool. whether or not operation succeeded
        """
        self.beginInsertRows(parent, position, position + rows - 1)

        for i in range(rows):
            self._colors.insert(position, QtGui.QColor("#000000"))

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        """
        Override: remove number of rows starting at a given row
        under certain parent (making it the child of the parent), when
        in a hierarchical structure from the model

        see also:
        https://doc.qt.io/qt-5/qabstractitemmodel.html#beginRemoveRows

        :param position: int. starting row position to remove
        :param rows: int. number of rows to remove
        :param parent: QModelIndex. index of the parent
        :return: bool. whether or not operation succeeded
        """
        self.beginRemoveRows(parent, position, position + rows - 1)

        for i in range(rows):
            value = self._colors[position]
            self._colors.remove(value)

        self.endRemoveRows()
        return True

    def insert(self, position, value, parent=QtCore.QModelIndex()):
        """
        Custom: insert an item/row at the given position with given value
        """
        self.beginInsertRows(parent, position, position+1)

        self._colors.insert(position, value)

        self.endInsertRows()
        return True


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    red = QtGui.QColor(255, 0, 0)
    green = QtGui.QColor(0, 255, 0)
    blue = QtGui.QColor(0, 0, 255)

    model = PaletteListModel([red, green, blue])
    model.insertRows(0, 5)

    # custom method
    model.insert(2, green)

    listView = QtWidgets.QListView()
    listView.show()
    listView.setModel(model)

    sys.exit(app.exec_())
