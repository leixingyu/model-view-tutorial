"""


# invisible root (for accessing top level items, even if top level items doesn't
# have a root, we pretend they share one)
# https://www.qtcentre.org/threads/70103-QModelIndex-value-for-the-root-of-a-tree-model
"""

from Qt import QtCore, QtGui

import node


class SceneGraphModel(QtCore.QAbstractItemModel):
    """INPUTS: Node, QObject"""

    def __init__(self, root, parent=None):
        super(SceneGraphModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        """
        Override: in this case, we want the column to be 1 regardless
        of the parent item

        :param parent:
        :return:
        """
        return 1

    def data(self, index, role):

        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name()

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return node.icon

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():

            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setName(value)

                return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Scenegraph"
            else:
                return "Typeinfo"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    """INPUTS: QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return the parent of the node with the given QModelIndex"""

    def parent(self, index):

        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column and parent node"""

    def index(self, row, column, parent):

        parentNode = self.getNode(parent)

        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    """CUSTOM"""
    """INPUTS: QModelIndex"""

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    """INPUTS: int, int, QModelIndex"""

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):

        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position+rows-1)

        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = node.Node("untitled"+str(childCount))
            success = parentNode.insertChild(position, childNode)

        self.endInsertRows()

        return success

    def insertLights(self, position, rows, parent=QtCore.QModelIndex()):

        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position+rows-1)

        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = node.LightNode("light"+str(childCount))
            success = parentNode.insertChild(position, childNode)

        self.endInsertRows()

        return success

    """INPUTS: int, int, QModelIndex"""

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):

        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position+rows-1)

        for row in range(rows):
            success = parentNode.removeChild(position)

        self.endRemoveRows()

        return success
