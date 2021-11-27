import os
import sys

from Qt import QtWidgets, QtCore, QtGui, QtXml
from Qt import _loadUi

import node
import highlighter
import models


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_FOLDER = os.path.join(MODULE_PATH, 'ui')


class DataWidgetMapperWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(DataWidgetMapperWindow, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'mainWindow.ui'), self)

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
        self.uiFilter.textChanged.connect(self._proxyModel.setFilterRegExp)

        self._propEditor = PropertiesEditor(self)
        self.layoutMain.addWidget(self._propEditor)
        self._propEditor.setModel(self._proxyModel)
        self.uiTree.selectionModel().currentChanged.connect(self._propEditor.setSelection)

        self._model.dataChanged.connect(self.updateXml)
        # Create our XMLHighlighter derived from QSyntaxHighlighter
        highlighter.XMLHighlighter(self.uiXml.document())
        self.updateXml()

    def updateXml(self):
        print "UPDATING XML"
        xml = self._rootNode.asXml()
        self.uiXml.setPlainText(xml)


class PropertiesEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PropertiesEditor, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'mainLayout.ui'), self)

        self._proxyModel = None

        self._nodeEditor = NodeEditor(self)
        self._lightEditor = LightEditor(self)
        self._cameraEditor = CameraEditor(self)
        self._transformEditor = TransformEditor(self)
        
        self.layoutNode.addWidget(self._nodeEditor)
        self.layoutSpecs.addWidget(self._lightEditor)
        self.layoutSpecs.addWidget(self._cameraEditor)
        self.layoutSpecs.addWidget(self._transformEditor)

        self._lightEditor.setVisible(False)
        self._cameraEditor.setVisible(False)
        self._transformEditor.setVisible(False)
               
    """INPUTS: QModelIndex, QModelIndex"""
    def setSelection(self, current, old):
        current = self._proxyModel.mapToSource(current)
        node = current.internalPointer()

        self._cameraEditor.setVisible(False)
        self._lightEditor.setVisible(False)
        self._transformEditor.setVisible(False)

        typeInfo = node.typeInfo() if node else None
            
        if typeInfo == "CAMERA":
            self._cameraEditor.setVisible(True)
        
        elif typeInfo == "LIGHT":
            self._lightEditor.setVisible(True)
             
        elif typeInfo == "TRANSFORM":
            self._transformEditor.setVisible(True)

        self._nodeEditor.setSelection(current)
        self._cameraEditor.setSelection(current)
        self._lightEditor.setSelection(current)
        self._transformEditor.setSelection(current)

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        
        self._nodeEditor.setModel(proxyModel)
        self._lightEditor.setModel(proxyModel)
        self._cameraEditor.setModel(proxyModel)
        self._transformEditor.setModel(proxyModel)


class NodeEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'nodeEditor.ui'), self)
        
        self._dataMapper = QtWidgets.QDataWidgetMapper()
        
    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiName, 0)
        self._dataMapper.addMapping(self.uiType, 1)
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)


class LightEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LightEditor, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'lightEditor.ui'), self)
        
        self._dataMapper = QtWidgets.QDataWidgetMapper()
        for i in node.LIGHT_SHAPES.names:
            if i != "End":
                self.uiShape.addItem(i)

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiLightIntensity, 2)
        self._dataMapper.addMapping(self.uiNear, 3)
        self._dataMapper.addMapping(self.uiFar, 4)
        self._dataMapper.addMapping(self.uiShadows, 5)
        self._dataMapper.addMapping(self.uiShape, 6, "currentIndex")
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        

class CameraEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CameraEditor, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'cameraEditor.ui'), self)
        
        self._dataMapper = QtWidgets.QDataWidgetMapper()
        
    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiMotionBlur, 2)
        self._dataMapper.addMapping(self.uiShakeIntensity, 3)
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        

class TransformEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TransformEditor, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'transformEditor.ui'), self)

        self._dataMapper = QtWidgets.QDataWidgetMapper()
        
    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiX, 2)
        self._dataMapper.addMapping(self.uiY, 3)
        self._dataMapper.addMapping(self.uiZ, 4)
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    wnd = DataWidgetMapperWindow()
    wnd.show()

    sys.exit(app.exec_())
