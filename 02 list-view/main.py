import sys

from Qt import QtGui, QtCore, QtWidgets


class PaletteListModel(QtCore.QAbstractListModel):
    def __init__(self, colors, parent=None):
        """
        Initialization

        :param colors: list. list of QColors
        :param parent: ???
        """
        QtCore.QAbstractListModel.__init__(self, parent)
        self._colors = colors

    def headerData(self, section, orientation, role):
        # orientation: indicates horizontal or vertical header
        # section:     indicates which index on the header
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return 'Palette'
            else:
                return 'Color {}'.format(section+1)

    def rowCount(self, parent):
        # parent: are for tree view with hierarchical structure
        return len(self._colors)

    def data(self, index, role):
        # display data for each index, of each data role
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
        return (QtCore.Qt.ItemIsEditable |
                QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        # set data for each index of the value, data role is set to edit role default
        if role == QtCore.Qt.EditRole:
            row = index.row()
            color = QtGui.QColor(value)
            if color.isValid():
                self._colors[row] = color
                # have to emit and dataChanged signal to sync with display
                self.dataChanged.emit(index, index)
                return True

        return False

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position+rows-1)

        for i in range(rows):
            self._colors.insert(position, QtGui.QColor("#000000"))

        self.endInsertRows()
        return True

    def insert(self, position, value, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position+1)

        self._colors.insert(position, value)

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position+rows-1)

        for i in range(rows):
            value = self._colors[position]
            self._colors.remove(value)

        self.endRemoveRows()
        return True


'''
when you call the model function, something like `self.model.update()`

1. the internal definition of update() or 
using the official setData() emits a data changed signal: dataChanged().emit()

2. the signal is caught by the view which uses the model: example: listView.setModel(model)

3. the view now looks at the model's data() definition

note: make sure the data structure defined in the model also updates according to your `update()` or `setData()` function

'''

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    red = QtGui.QColor(255, 0, 0)
    green = QtGui.QColor(0, 255, 0)
    blue = QtGui.QColor(0, 0, 255)

    model = PaletteListModel([red, green, blue])
    model.insertRows(0, 5)

    model.insert(2, green)

    listView = QtWidgets.QListView()
    listView.show()
    listView.setModel(model)

    sys.exit(app.exec_())
