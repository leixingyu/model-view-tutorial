import os

from Qt import QtGui


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(MODULE_PATH, 'icons')


class Node(object):
    def __init__(self, name, parent=None):
        self._name = name
        self._children = []
        self._parent = parent
        self._icon = None

        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        return "NODE"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    @property
    def icon(self):
        return self._icon

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):

        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"

        output += "|------"+self._name+"\n"

        for child in self._children:
            output += child.log(tabLevel)

        tabLevel -= 1
        output += "\n"

        return output

    def __repr__(self):
        return self.log()


class TransformNode(Node):

    def __init__(self, name, parent=None):
        super(TransformNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'transform.png')
        ))

    def typeInfo(self):
        return "TRANSFORM"


class CameraNode(Node):

    def __init__(self, name, parent=None):
        super(CameraNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'camera.png')
        ))

    def typeInfo(self):
        return "CAMERA"


class LightNode(Node):

    def __init__(self, name, parent=None):
        super(LightNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'light.png')
        ))

    def typeInfo(self):
        return "LIGHT"
