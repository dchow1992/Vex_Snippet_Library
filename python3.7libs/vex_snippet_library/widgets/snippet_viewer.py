import os

import json

import sys

from PySide2 import QtWidgets, QtGui, QtCore

from vex_snippet_library.widgets import button_table


class SnippetViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SnippetViewer, self).__init__(parent)
        self.icons = os.path.abspath(
            os.path.join(__file__, '..', '..', '..', '..', 'icons'))
        self.filter_text = ''
        self._init_ui()

    def _init_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)

        self.add_btn = QtWidgets.QPushButton()
        self.add_btn.setToolTip('Add New Snippet')
        icon = QtGui.QIcon(
            QtGui.QPixmap(os.path.join(self.icons, 'add.svg')))
        self.add_btn.setIcon(icon)

        self.del_btn = QtWidgets.QPushButton()
        self.del_btn.setToolTip('Delete Selected Snippet')
        icon = QtGui.QIcon(
            QtGui.QPixmap(os.path.join(self.icons, 'delete.svg')))
        self.del_btn.setIcon(icon)

        self.search_lbl = QtWidgets.QLabel('Filter')
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.textChanged.connect(self.filter_snippets)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_lbl)
        search_layout.addWidget(self.search_edit)

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
        self.table.filter.setFilterRegExp(QtCore.QRegExp(
            self.search_edit.text(),
            QtCore.Qt.CaseInsensitive,
            QtCore.QRegExp.FixedString))

    def setEnabled(self, mode=True):
        self.add_btn.setEnabled(mode)
        self.del_btn.setEnabled(mode)
        self.search_edit.setEnabled(mode)
        self.table.setEnabled(mode)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = SnippetViewer()
    w.show()
    sys.exit(app.exec_())
