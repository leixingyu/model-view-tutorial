import os
import sys

from Qt import QtWidgets, QtCore
from Qt import _loadUi

import model
import node


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_FILE = os.path.join(MODULE_PATH, 'main.ui')


class TreeModelMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(TreeModelMainWindow, self).__init__()
        _loadUi(UI_FILE, self)

        # this node will never get displayed, also known as invisible root
        rootNode = node.Node("Hips")
        childNode0 = node.TransformNode("RightPirateLeg", rootNode)
        childNode1 = node.Node("RightPirateLeg_END", childNode0)
        childNode2 = node.CameraNode("LeftFemur", rootNode)
        childNode3 = node.Node("LeftTibia", childNode2)
        childNode4 = node.Node("LeftFoot", childNode3)
        childNode5 = node.LightNode("LeftFoot_END", childNode4)

        # the proxy model is between data model and the view
        # view <------> proxy model <------> data model

        self._proxyModel = QtCore.QSortFilterProxyModel()

        self._model = model.SceneGraphModel(rootNode)
        self._model.insertLights(0, 10)

        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.centralTreeView.setModel(self._proxyModel)
        self.filterLineEdit.textChanged.connect(self._proxyModel.setFilterRegExp)
        self.centralTreeView.setSortingEnabled(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = TreeModelMainWindow()
    win.show()
    sys.exit(app.exec_())
