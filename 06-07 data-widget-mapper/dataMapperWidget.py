"""
The supplement class for custom DataMapperWidget to be displayed and connected
in the main window.
"""

import os

from Qt import QtWidgets, QtCore, QtGui, QtXml
from Qt import _loadUi

import node


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_FOLDER = os.path.join(MODULE_PATH, 'ui')


class DataMapperWidget(QtWidgets.QWidget):
    """
    Abstract class for widget with data mapper setup
    """
    def __init__(self, model, parent=None):
        """
        Initialization creates a QDataWidgetMapper and connects it with
        the data model

        :param model: QAbstractItemModel. model to be connected
        :param parent: QWidget. parent widget for placing the current widget
        """
        super(DataMapperWidget, self).__init__(parent)
        self._dataMapper = QtWidgets.QDataWidgetMapper()

        # proxy model needs to be converted to source model
        # https://doc.qt.io/qt-5/qdatawidgetmapper.html#setModel
        if isinstance(model, QtCore.QAbstractProxyModel):
            model = model.sourceModel()
        self._dataMapper.setModel(model)

    def addMapping(self):
        """
        Custom: this sets mapping for specific widget item to specific
        model item.

        # https://doc.qt.io/qt-5/qdatawidgetmapper.html#addMapping
        """
        pass

    def setSelection(self, current):
        """
        Custom: this sets the dataMapper index to the updated item that
        is currently selected, so it knows which item/node to display

        # https://doc.qt.io/qt-5/qdatawidgetmapper.html#setRootIndex
        # https://doc.qt.io/qt-5/qdatawidgetmapper.html#setCurrentModelIndex

        :param current: QModelIndex. current model item index being selected
        """
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)


class NodeEditor(DataMapperWidget):
    def __init__(self, model, parent=None):
        super(NodeEditor, self).__init__(model, parent)
        _loadUi(os.path.join(UI_FOLDER, 'nodeEditor.ui'), self)
        self.addMapping()

    def addMapping(self):
        self._dataMapper.addMapping(self.uiName, 0)
        self._dataMapper.addMapping(self.uiType, 1)


class LightEditor(DataMapperWidget):
    def __init__(self, model, parent=None):
        super(LightEditor, self).__init__(model, parent)
        _loadUi(os.path.join(UI_FOLDER, 'lightEditor.ui'), self)

        for shape in node.LightShapes:
            self.uiShape.addItem(shape.name)
        self.addMapping()

    def addMapping(self):
        self._dataMapper.addMapping(self.uiLightIntensity, 2)
        self._dataMapper.addMapping(self.uiNear, 3)
        self._dataMapper.addMapping(self.uiFar, 4)
        self._dataMapper.addMapping(self.uiShadows, 5)
        self._dataMapper.addMapping(self.uiShape, 6, "currentIndex")


class CameraEditor(DataMapperWidget):
    def __init__(self, model, parent=None):
        super(CameraEditor, self).__init__(model, parent)
        _loadUi(os.path.join(UI_FOLDER, 'cameraEditor.ui'), self)

        self.addMapping()

    def addMapping(self):
        self._dataMapper.addMapping(self.uiMotionBlur, 2)
        self._dataMapper.addMapping(self.uiShakeIntensity, 3)


class TransformEditor(DataMapperWidget):
    def __init__(self, model, parent=None):
        super(TransformEditor, self).__init__(model, parent)
        _loadUi(os.path.join(UI_FOLDER, 'transformEditor.ui'), self)

        self.addMapping()

    def addMapping(self):
        self._dataMapper.addMapping(self.uiX, 2)
        self._dataMapper.addMapping(self.uiY, 3)
        self._dataMapper.addMapping(self.uiZ, 4)
