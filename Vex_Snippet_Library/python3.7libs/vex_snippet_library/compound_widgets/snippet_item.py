from PySide2 import QtWidgets

import hou


class SnippetItem(QtWidgets.QWidget):
    def __init__(self):
        super(SnippetItem, self).__init__()

        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel('Item')
        self.copy_btn = QtWidgets.QPushButton('Copy')

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.copy_btn)
        self.setLayout(self.layout)
