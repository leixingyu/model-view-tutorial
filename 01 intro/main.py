"""
Demonstrate how data accessed through a model is shared across multiple views
"""

import sys

from Qt import QtGui, QtCore, QtWidgets


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    data = ['one', 'two', 'three']
    model = QtCore.QStringListModel(data)

    listView = QtWidgets.QListView()
    listView.setModel(model)
    listView.show()

    combobox = QtWidgets.QComboBox()
    combobox.setModel(model)
    combobox.show()

    sys.exit(app.exec_())
