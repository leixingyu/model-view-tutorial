"""
The node module is for creating node data structure/class that supports
hierarchical model. Each node object reflects to an abstract item which
has child and parent relationships
"""

import os

from Qt import QtGui


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(MODULE_PATH, 'icons')


class Node(object):
    def __init__(self, name, parent=None):
        self._name = name
        self._children = list()
        self._parent = parent
        self._icon = None
        self._type = "node"

        if parent is not None:
            parent.appendChild(self)

    def log(self, tabLevel=-1):
        output = ""
        tabLevel += 1

        output += "\t" * tabLevel
        output += "|------{}\n".format(self._name)

        for child in self._children:
            output += child.log(tabLevel)

        return output

    def __repr__(self):
        return self.log()

    @property
    def name(self):
        """
        :return str. name of the node to be displayed
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        :param value: str. node name
        """
        self._name = value

    @property
    def childCount(self):
        """
        :return: int. number of children of the current node
        """
        return len(self._children)

    @property
    def parent(self):
        """
        :return: Node. the parent of the current node
        """
        return self._parent

    @property
    def icon(self):
        """
        :return: QIcon. node icon to be displayed in decoration role
        """
        return self._icon

    @property
    def type(self):
        """
        :return: str. node type
        """
        return self._type

    def appendChild(self, child):
        """
        Append a child under current item

        :param child: Node. child node to append
        """
        self._children.append(child)

    def insertChild(self, row, child):
        """
        Insert a child under current item after certain row index

        :param row: int. row index to insert
        :return: bool. whether the operation succeeded
        """
        if row < 0 or row > len(self._children):
            return False

        self._children.insert(row, child)
        child._parent = self
        return True

    def removeChild(self, row):
        """
        Remove the child of the current item on certain row
        
        :param row: int. row index to remove
        :return: bool. whether the operation succeeded
        """
        if row < 0 or row > len(self._children):
            return False

        child = self._children.pop(row)
        child._parent = None
        return True

    def child(self, row):
        """
        Get the child of the current item on certain row
        
        :param row: int. row/index of the child
        :return: Node. child node
        """
        return self._children[row]

    def row(self):
        """
        :return: index of the current item under its parent 
        """
        if self._parent:
            return self._parent._children.index(self)
        return 0


class TransformNode(Node):
    def __init__(self, name, parent=None):
        super(TransformNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'transform.png')
        ))
        self._type = 'transform'


class CameraNode(Node):
    def __init__(self, name, parent=None):
        super(CameraNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'camera.png')
        ))
        self._type = 'camera'


class LightNode(Node):
    def __init__(self, name, parent=None):
        super(LightNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'light.png')
        ))
        self._type = 'light'
