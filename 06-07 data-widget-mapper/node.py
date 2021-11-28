"""
The node module is for creating node data structure/class that supports
hierarchical model. Each node object reflects to an abstract item which
has child and parent relationships; Different types of node also has its
own custom properties
"""

import os
from enum import IntEnum, unique

from Qt import QtGui, QtXml


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(MODULE_PATH, 'icons')


@unique
class LightShapes(IntEnum):
    POINT = 0
    SPOT = 1
    DIRECTIONAL = 2
    AREA = 3
    VOLUMETRIC = 4


class Node(object):
    def __init__(self, name, parent=None):
        super(Node, self).__init__()
        self._name = name
        self._children = list()
        self._parent = parent
        self._icon = None
        self._type = 'node'
        
        if parent:
            parent.addChild(self)

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
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def childCount(self):
        return len(self._children)

    @property
    def parent(self):
        return self._parent

    @property
    def row(self):
        if self.parent:
            return self.parent._children.index(self)
        return 0

    @property
    def icon(self):
        return self._icon

    # ------------ XML Generation ---------------#

    def attrs(self):
        """
        Parse class property list and values used for generating xml

        :return: dict. property names and values
        """
        classes = self.__class__.__mro__
        kv = dict()
        for cls in classes:
            # get property name and object
            for k, v in cls.__dict__.iteritems():
                if isinstance(v, property):
                    # skip properties in xml parsing
                    if k in ['icon', 'type', 'parent', 'row', 'childCount']:
                        break
                    kv[k] = getattr(self, k)
        return kv

    def asXml(self):
        """
        Return the xml formatting of the node hierarchy and all of its
        attribute/property names and values, used on root node

        :return: str. output string formatted as xml
        """
        doc = QtXml.QDomDocument()
        node = doc.createElement(self.type)
        doc.appendChild(node)
        for child in self._children:
            child._recurseXml(doc, node)

        return doc.toString(indent=4)

    def _recurseXml(self, doc, parent):
        """
        Recursively generate xml elements

        :param doc: QDomDocument. xml root
        :param parent: QDomElement. xml parent element
        """
        node = doc.createElement(self.type)
        parent.appendChild(node)
        attrs = self.attrs().iteritems()
        for k, v in attrs:
            node.setAttribute(k, v)

        for child in self._children:
            child._recurseXml(doc, node)

    # -------------- Child insert/remove -------------- #

    def addChild(self, child):
        self._children.append(child)
        child._parent = self

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

    def child(self, row):
        return self._children[row]

    # ---------------- Data <-> Model handling ------------------- #

    def data(self, column):
        """
        Custom: return underlying value of the current Node based on column,
        used for displaying data used in the model

        :param column: int. column index of the model
        :return:
        """
        if column == 0:
            return self.name
        elif column == 1:
            return self.type
    
    def setData(self, column, value):
        """
        Custom: set values for the current Node based on column, input value,
        used for editing data used in the model

        :param column: int. column index of the model
        :param value: QVariant. value for a certain property of the item
        """
        if column == 0:
            self.name = value


class TransformNode(Node):
    def __init__(self, name, parent=None):
        super(TransformNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'transform.png')
        ))
        self._type = 'transform'
        self._x = 0
        self._y = 0
        self._z = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self.y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self.z = value

    def data(self, column):
        r = super(TransformNode, self).data(column)
        if column == 2:
            r = self.x
        elif column == 3:
            r = self.y
        elif column == 4:
            r = self.z
        return r
    
    def setData(self, column, value):
        super(TransformNode, self).setData(column, value)
        if column == 2:
            self.x = value
        elif column == 3:
            self.y = value
        elif column == 4:
            self.z = value


class CameraNode(Node):
    def __init__(self, name, parent=None):
        super(CameraNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'camera.png')
        ))
        self._type = 'camera'
        self._motionBlur = True
        self._shakeIntensity = 50.0

    @property
    def motionBlur(self):
        return self._motionBlur
    
    @motionBlur.setter
    def motionBlur(self, value):
        self._motionBlur = value
     
    @property
    def shakeIntensity(self):
        return self._shakeIntensity
    
    @shakeIntensity.setter
    def shakeIntensity(self, value):
        self._shakeIntensity = value
        
    def data(self, column):
        r = super(CameraNode, self).data(column)
        if column == 2:
            r = self.motionBlur
        elif column == 3:
            r = self.shakeIntensity
        
        return r
    
    def setData(self, column, value):
        super(CameraNode, self).setData(column, value)
        if column == 2:
            self.motionBlur = value
        elif column == 3:
            self.shakeIntensity = value


class LightNode(Node):
    def __init__(self, name, parent=None):
        super(LightNode, self).__init__(name, parent)
        self._icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(ICON_PATH, 'light.png')
        ))
        self._type = 'light'
        self._intensity = 1.0
        self._nearRange = 40.0
        self._farRange = 80.0
        self._castShadows = True
        self._shape = LightShapes(0)

    @property
    def intensity(self):
        return self._intensity
    
    @intensity.setter
    def intensity(self, value):
        self._intensity = value
    
    @property
    def nearRange(self):
        return self._nearRange
    
    @nearRange.setter
    def nearRange(self, value):
        self._nearRange = value

    @property
    def farRange(self):
        return self._farRange

    @farRange.setter
    def farRange(self, value):
        self._farRange = value

    @property
    def castShadows(self):
        return self._castShadows

    @castShadows.setter
    def castShadows(self, value):
        self._castShadows = value

    @property
    def shape(self):
        return self._shape.name

    @shape.setter
    def shape(self, value):
        self._shape = value

    def data(self, column):
        r = super(LightNode, self).data(column)
        if column == 2:
            r = self.intensity
        elif column == 3:
            r = self.nearRange
        elif column == 4:
            r = self.farRange
        elif column == 5:
            r = self.castShadows
        elif column == 6:
            r = self.shape
        
        return r
    
    def setData(self, column, value):
        super(LightNode, self).setData(column, value)
        
        if column == 2:
            self.intensity = value
        elif column == 3:
            self.nearRange = value
        elif column == 4:
            self.farRange = value
        elif column == 5:
            self.castShadows = value
        elif column == 6:
            self.shape = LightShapes(value)
