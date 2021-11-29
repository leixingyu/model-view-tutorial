"""
This model is similar to previous lesson supporting our custom node, the only
difference being the data() and setData() method lets the node to handle it
internally
"""

from Qt import QtCore, QtGui

import node


class SceneGraphModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1

    def __init__(self, root, parent=None):
        super(SceneGraphModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        """
        Override: due to the complexity of the Node type, it is better to pass
        the value for the Node to return data() for display internally
        """
        if not index.isValid():
            return None

        currentNode = index.internalPointer()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            # not all column needs to be displayed in the view, more columns
            # can store different types of data of the node, and they can be
            # accessed in other places; in our case, dataWidgetMapper maps
            # data from multiple columns on multiple ui elements for display
            return currentNode.data(index.column())
 
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return currentNode.icon
            
        if role == SceneGraphModel.sortRole:
            return currentNode.type

        if role == SceneGraphModel.filterRole:
            return currentNode.type

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Override: due to the complexity of the Node type, it is better to pass
        the value for the Node to handle setData() for editing internally
        """
        if index.isValid():
            currentNode = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                currentNode.setData(index.column(), value)
                self.dataChanged.emit(index, index)
                return True
            
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Scene Graph"
            else:
                return "Type Info"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def parent(self, index):
        currentNode = self.getNode(index)
        parentNode = currentNode.parent
        
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        
        return self.createIndex(parentNode.row, 0, parentNode)

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        currentNode = parentNode.child(row)
        if currentNode:
            return self.createIndex(row, column, currentNode)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        """
        Custom method
        """
        if index.isValid():
            currentNode = index.internalPointer()
            if currentNode:
                return currentNode
        return self._rootNode

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = node.Node("untitled" + str(childCount))
            parentNode.insertChild(position, childNode)

        self.endInsertRows()
        return True
    
    def insertLights(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = node.LightNode("light" + str(childCount))
            parentNode.insertChild(position, childNode)
        
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        for row in range(rows):
            parentNode.removeChild(position)

        self.endRemoveRows()
        return True
