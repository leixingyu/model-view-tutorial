"""
The main window for instantiate different types of nodes to be passed in
our hierarchical model, and displayed in the tree view. additionally: a custom
xml viewer, and dynamic property widget using QDataWidgetMapper

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
import model
import dataMapperWidget


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

        self._model = model.SceneGraphModel(self._rootNode, self)

        # proxy model
        self._proxyModel = QtCore.QSortFilterProxyModel(self)
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._proxyModel.setSortRole(model.SceneGraphModel.sortRole)
        self._proxyModel.setFilterRole(model.SceneGraphModel.filterRole)
        self._proxyModel.setFilterKeyColumn(0)
        
        self.uiTree.setModel(self._proxyModel)

        # add container layout for holding property widget
        self._propEditor = PropertyContainerWidget(self._proxyModel, self)
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


class PropertyContainerWidget(QtWidgets.QWidget):
    def __init__(self, model, parent=None):
        super(PropertyContainerWidget, self).__init__(parent)
        _loadUi(os.path.join(UI_FOLDER, 'mainLayout.ui'), self)

        self._proxyModel = model

        self._nodeEditor = dataMapperWidget.NodeEditor(model, self)
        self._lightEditor = dataMapperWidget.LightEditor(model, self)
        self._cameraEditor = dataMapperWidget.CameraEditor(model, self)
        self._transformEditor = dataMapperWidget.TransformEditor(model, self)

        # add widget and hide them
        self.layoutNode.addWidget(self._nodeEditor)
        self.layoutSpecs.addWidget(self._lightEditor)
        self.layoutSpecs.addWidget(self._cameraEditor)
        self.layoutSpecs.addWidget(self._transformEditor)

        self._lightEditor.setVisible(False)
        self._cameraEditor.setVisible(False)
        self._transformEditor.setVisible(False)

    def setSelection(self, current, old):
        """
        Custom: update selection whenever currentChanged() signal is emitted
        https://doc.qt.io/qt-5/qitemselectionmodel.html#currentChanged

        update which property widget is displayed and display the data
        of the node corresponding to the current model item index by calling
        subsequent setSelection() method in those widget class

        :param current: QModelIndex. current model item index being selected
        :param old: QModelIndex. previous model item index
        """
        # update selection and display based on node selected
        currentIndex = self._proxyModel.mapToSource(current)
        currentNode = currentIndex.internalPointer()

        # node editor always get displayed
        self._nodeEditor.setSelection(currentIndex)

        self._cameraEditor.setVisible(False)
        self._lightEditor.setVisible(False)
        self._transformEditor.setVisible(False)

        ntype = currentNode.type if currentNode else None
        if ntype == "camera":
            self._cameraEditor.setVisible(True)
            self._cameraEditor.setSelection(currentIndex)
        
        elif ntype == "light":
            self._lightEditor.setVisible(True)
            self._lightEditor.setSelection(currentIndex)
             
        elif ntype == "transform":
            self._transformEditor.setVisible(True)
            self._transformEditor.setSelection(currentIndex)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
