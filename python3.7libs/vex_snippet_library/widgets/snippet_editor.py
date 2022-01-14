import os

from PySide2 import QtWidgets, QtCore, QtGui

from . import vex_editor


class SnippetEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SnippetEditor, self).__init__(parent)
        self.editable = False
        self._init_ui()

    def _init_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        root = os.path.abspath(os.path.join(__file__, '..', '..', '..', '..'))
        icons = os.path.join(root, 'resources', 'icons')

        self.edit_btn = QtWidgets.QPushButton('')
        self.edit_btn.setToolTip('Allow Editing')
        icon = QtGui.QIcon(
            QtGui.QPixmap(os.path.join(icons, 'edit.png')))
        self.edit_btn.setIcon(icon)
        self.edit_btn.clicked.connect(self.edit_btn_callback)
        self.edit_btn.setStyleSheet(
            '''
            QPushButton:disabled
            {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0.0 rgba(64, 164, 64, 40%),
                                            stop: 1.0 rgba(38, 255, 38, 40%));
            }
            ''')

        self.save_btn = QtWidgets.QPushButton('')
        self.save_btn.setToolTip('Save Changes')
        icon = QtGui.QIcon(os.path.join(icons, 'save.png'))
        self.save_btn.setIcon(icon)
        self.save_btn.clicked.connect(self.save_btn_callback)

        self.cancel_btn = QtWidgets.QPushButton('')
        self.cancel_btn.setToolTip('Discard Changes')
        icon = QtGui.QIcon(os.path.join(icons, 'cancel.png'))
        self.cancel_btn.setIcon(icon)
        self.cancel_btn.clicked.connect(self.cancel_btn_callback)

        self.combo_lbl = QtWidgets.QLabel('Run Over')
        self.combo = QtWidgets.QComboBox()
        combo_items = [
            'Detail',
            'Primitives',
            'Points',
            'Vertices'
        ]
        self.combo.addItems(combo_items)
        self.combo.setCurrentIndex(2)

        self.editor = vex_editor.VexEditor(self)

        # defaults
        self.editor.disable_editor()
        self.combo.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.combo_lbl.setEnabled(False)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        combo_layout = QtWidgets.QHBoxLayout()
        combo_layout.addSpacing(12)
        combo_layout.addWidget(self.combo_lbl)
        combo_layout.addWidget(self.combo)
        combo_layout.addStretch()

        self.layout.addLayout(btn_layout)
        self.layout.addLayout(combo_layout)
        self.layout.addWidget(self.editor)

    def edit_btn_callback(self):
        if not self.editable:
            self.editable = True
            self.editor.enable_editor()
            self.save_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            self.combo.setEnabled(True)
            self.combo_lbl.setEnabled(True)
            self.edit_btn.setEnabled(False)
            self.editor.setFocus()

    def save_btn_callback(self):
        self.editable = False
        self.editor.disable_editor()
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.combo.setEnabled(False)
        self.combo_lbl.setEnabled(False)
        self.edit_btn.setEnabled(True)

    def cancel_btn_callback(self):
        self.editable = False
        self.editor.disable_editor()
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.combo.setEnabled(False)
        self.combo_lbl.setEnabled(False)
        self.edit_btn.setEnabled(True)
