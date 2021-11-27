"""
A demonstration on how to create QAbstractItemModel used in QTreeView

The major difference of a hierarchical model is the concept of parent. A
model with parent can still have rows and column, but it is corresponding
to certain parent. (for instance: in a list model, row index refers to the
row index of the entire list while with parent, the row index refers to
the row under certain parent, which is the child row index)

Also something worth noting is invisible root, this root node is never displayed
but is used for accessing top-level items.
Even if top-level item(s) doesn't have a root, we pretend they share this
invisible root.
https://www.qtcentre.org/threads/70103-QModelIndex-value-for-the-root-of-a-tree-model
"""

from Qt import QtCore, QtGui

import node


class SceneGraphModel(QtCore.QAbstractItemModel):
    """INPUTS: currentNode, QObject"""

    def __init__(self, root):
        """
        Initialization

        :param root: Node. invisible root node for accessing top level items
        """
        super(SceneGraphModel, self).__init__()
        self._rootNode = root

    def rowCount(self, parent):
        """
        Override: row/child count of the certain parent

        :param parent: Node. parent node
        :return: int. number of the children/rows of the parent
        """
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount

    def columnCount(self, parent):
        """
        Override: column of the item under certain parent
        in this case, we want the column to be 1 regardless
        of the parent item

        :param parent: Node. parent node
        :return: int. number of columns
        """
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        currentNode = index.internalPointer()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return currentNode.name
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return currentNode.icon

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                currentNode = index.internalPointer()
                currentNode.setName(value)
                return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Scene Graph"
            else:
                return "Type Info"

    def flags(self, index):
        return (QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsEditable)

    def parent(self, index):
        """
        Override: return a QModelIndex of the parent node of the given index

        :param index: QModelIndex. current node index
        :return: QModelIndex. parent node index
        """
        currentNode = self.getNode(index)
        parentNode = currentNode.parent
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        """
        Override: return a QModelIndex that corresponds to the given row,
        column and parent node

        :param row: int. row index
        :param column: int. column index
        :param parent: QModelIndex. parent node index
        :return: QModelIndex. current node index
        """
        parentNode = self.getNode(parent)
        currentNode = parentNode.child(row)
        if currentNode:
            return self.createIndex(row, column, currentNode)
        else:
            return QtCore.QModelIndex()

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        """
        Override: the method now inserts rows/children to certain parent
        """
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position+rows-1)
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = node.currentNode("untitled"+str(childCount))
            parentNode.insertChild(position, childNode)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        """
        Override: the method now removes rows/children to certain parent
        """
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position+rows-1)
        for row in range(rows):
            parentNode.removeChild(position)
        self.endRemoveRows()
        return True

    def insertLights(self, position, rows, parent=QtCore.QModelIndex()):
        """
        Insert light nodes as rows/children to certain parent

        we are declaring custom method for inserting node, as long as we
        obey the beginInsertRows() and endInsertRows() structure
        """
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position+rows-1)
        for row in range(rows):
            childCount = parentNode.childCount
            childNode = node.LightNode("light"+str(childCount))
            parentNode.insertChild(position, childNode)
        self.endInsertRows()
        return True

    def getNode(self, index):
        """
        Helper method of getting the node object of a given index

        :param index: QModelIndex. given index to retrieve node
        :return: Node. node of given index
        """
        if index.isValid():
            currentNode = index.internalPointer()
            if currentNode:
                return currentNode

        return self._rootNode
