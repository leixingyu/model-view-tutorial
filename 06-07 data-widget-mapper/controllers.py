"""


The xml serves only for the purpose of displaying the data, which is a one-way
direction data communication

selectionModel()
qt docs: https://doc.qt.io/qt-5/qabstractitemview.html#selectionModel

https://stackoverflow.com/questions/53483965/qtreeview-selectionchanged-trigger-method
"""

import os
import sys

from Qt import QtWidgets, QtCore, QtGui, QtXml
from Qt import _loadUi

import node
import highlighter
import models


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_FOLDER = os.path.join(MODULE_PATH, 'ui')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'mainWindow.ui'), self)

        # node and model setup
        self._rootNode = node.Node("Root")
        childNode0 = node.TransformNode("A", self._rootNode)
        childNode1 = node.LightNode("B", self._rootNode)
        childNode2 = node.CameraNode("C", self._rootNode)
        childNode3 = node.TransformNode("D", self._rootNode)
        childNode4 = node.LightNode("E", self._rootNode)
        childNode5 = node.CameraNode("F", self._rootNode)
        childNode6 = node.TransformNode("G", childNode5)
        childNode7 = node.LightNode("H", childNode6)
        childNode8 = node.CameraNode("I", childNode7)

        self._model = models.SceneGraphModel(self._rootNode, self)

        # proxy model
        self._proxyModel = QtCore.QSortFilterProxyModel(self)
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._proxyModel.setSortRole(models.SceneGraphModel.sortRole)
        self._proxyModel.setFilterRole(models.SceneGraphModel.filterRole)
        self._proxyModel.setFilterKeyColumn(0)
        
        self.uiTree.setModel(self._proxyModel)

        # add main layout
        self._propEditor = PropertiesEditor(self._proxyModel, self)
        self.layoutMain.addWidget(self._propEditor)

        # for xml highlighting
        highlighter.XMLHighlighter(self.uiXml.document())

        # connect signals
        self._model.dataChanged.connect(self.updateXml)
        self.uiTree.selectionModel().currentChanged.connect(self._propEditor.setSelection)
        self.uiFilter.textChanged.connect(self._proxyModel.setFilterRegExp)

        # initialize xml
        self.updateXml()

    def updateXml(self):
        """
        Refresh xml ui field with the xml formatting from the lastest node
        attribute dictionary
        """
        xml = self._rootNode.asXml()
        self.uiXml.setPlainText(xml)


class DataMapperWidget(QtWidgets.QWidget):
    """
    Abstract class for widget with data mapper setup
    """
    def __init__(self, model, parent=None):
        super(DataMapperWidget, self).__init__(parent)
        self._dataMapper = QtWidgets.QDataWidgetMapper()

        # https://doc.qt.io/qt-5/qdatawidgetmapper.html#setModel
        if isinstance(model, QtCore.QAbstractProxyModel):
            model = model.sourceModel()
        self._dataMapper.setModel(model)

    def addMapping(self):
        # https://doc.qt.io/qt-5/qdatawidgetmapper.html#addMapping
        self._dataMapper.addMapping(self.uiName, 0)
        self._dataMapper.addMapping(self.uiType, 1)

    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        # https://doc.qt.io/qt-5/qdatawidgetmapper.html#setRootIndex
        # https://doc.qt.io/qt-5/qdatawidgetmapper.html#setCurrentModelIndex
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)


class PropertiesEditor(QtWidgets.QWidget):
    def __init__(self, model, parent=None):
        super(PropertiesEditor, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'mainLayout.ui'), self)

        self._proxyModel = model

        self._nodeEditor = NodeEditor(model, self)
        self._lightEditor = LightEditor(model, self)
        self._cameraEditor = CameraEditor(model, self)
        self._transformEditor = TransformEditor(model, self)
        
        self.layoutNode.addWidget(self._nodeEditor)
        self.layoutSpecs.addWidget(self._lightEditor)
        self.layoutSpecs.addWidget(self._cameraEditor)
        self.layoutSpecs.addWidget(self._transformEditor)

        self._lightEditor.setVisible(False)
        self._cameraEditor.setVisible(False)
        self._transformEditor.setVisible(False)

    """INPUTS: QModelIndex, QModelIndex"""
    # https://doc.qt.io/qt-5/qitemselectionmodel.html#currentChanged
    def setSelection(self, current, old):
        # update selection and display based on node selected
        current = self._proxyModel.mapToSource(current)
        currentNode = current.internalPointer()

        # node editor always get displayed
        self._nodeEditor.setSelection(current)

        self._cameraEditor.setVisible(False)
        self._lightEditor.setVisible(False)
        self._transformEditor.setVisible(False)

        ntype = currentNode.type if currentNode else None
        if ntype == "camera":
            self._cameraEditor.setVisible(True)
            self._cameraEditor.setSelection(current)
        
        elif ntype == "light":
            self._lightEditor.setVisible(True)
            self._lightEditor.setSelection(current)
             
        elif ntype == "transform":
            self._transformEditor.setVisible(True)
            self._transformEditor.setSelection(current)


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
        
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
