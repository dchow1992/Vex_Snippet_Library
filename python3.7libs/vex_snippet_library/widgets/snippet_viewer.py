import os

import json

from PySide2 import QtWidgets, QtGui, QtCore

from . import button_table


class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.Signal(str)

    def __init__(self, width, height):
        super(ClickableLabel, self).__init__()
        self.setObjectName('ClickableLabel')

    def mousePressEvent(self, event):
        self.clicked.emit(self.objectName())


class SnippetViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SnippetViewer, self).__init__(parent)
        self.icons = os.path.abspath(
            os.path.join(__file__, '..', '..', '..', '..', 'icons'))
        self.filter_text = ''
        self._init_ui()

    def _init_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        root = os.path.abspath(os.path.join(__file__, '..', '..', '..', '..'))
        icons = os.path.join(root, 'resources', 'icons')

        self.add_btn = QtWidgets.QPushButton()
        self.add_btn.setToolTip('Add New Snippet')
        icon = QtGui.QIcon(os.path.join(icons, 'add.svg'))
        self.add_btn.setIcon(icon)

        self.del_btn = QtWidgets.QPushButton()
        self.del_btn.setToolTip('Delete Selected Snippet')
        icon = QtGui.QIcon(os.path.join(icons, 'delete.svg'))
        self.del_btn.setIcon(icon)

        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText('Filter')
        self.search_edit.textChanged.connect(self.filter_snippets)

        self.clear_btn = ClickableLabel(35, 35)
        icon = QtGui.QIcon(
            QtGui.QPixmap(os.path.join(icons, 'clear_filter.svg')))
        pixmap = icon.pixmap(QtCore.QSize(64, 64))
        self.clear_btn.setPixmap(pixmap)
        self.clear_btn.clicked.connect(self.clear_btn_callback)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.clear_btn)

        self.table = button_table.ButtonTable()
        self.table.setStyleSheet(
            '''
            QTableView
            {
                font-size: 15px;
            }
            QTableView::item
            {
                border-right: 0;
                border-left: 0;
                border-bottom: 0;
            }
            ''')

        self.layout.addLayout(btn_layout)
        self.layout.addLayout(search_layout)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.table)

    def filter_snippets(self):
        self.table.model.beginResetModel()
        self.table.filter.setFilterRegExp(QtCore.QRegExp(
            self.search_edit.text(),
            QtCore.Qt.CaseInsensitive,
            QtCore.QRegExp.FixedString))
        self.table.model.endResetModel()

    def setEnabled(self, mode=True):
        self.add_btn.setEnabled(mode)
        self.del_btn.setEnabled(mode)
        self.search_edit.setEnabled(mode)
        self.table.setEnabled(mode)

    def clear_btn_callback(self):
        self.search_edit.setText('')
