import os

import sys

import string

import json

# tmp venv code
sys.path.append('C:/Users/dchow/Documents/_GitHub/Vex_Snippet_Library/python3.7libs')
# end tmp code

from PySide2 import QtWidgets, QtCore

from vex_snippet_library.widgets import snippet_editor

from vex_snippet_library.widgets import snippet_viewer


class VexSnippetLibrary(QtWidgets.QWidget):
    def __init__(self):
        super(VexSnippetLibrary, self).__init__()
        self._creating = False
        self._editing = False
        self._snippet_name = ''
        self._snippet_data = {}
        self.prev_idx = None
        self.root = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
        self.json_path = os.path.join(self.root, 'json')
        self._init_ui()
        self.load_snippets()

    @property
    def creating(self):
        return self._creating

    @creating.setter
    def creating(self, value):
        self._creating = value

    @property
    def editing(self):
        return self._editing

    @editing.setter
    def editing(self, value):
        self._editing = value

    @property
    def snippet_name(self):
        return self._snippet_name

    @snippet_name.setter
    def snippet_name(self, value):
        self._snippet_name = value

    @property
    def snippet_data(self):
        return self._snippet_data

    @snippet_data.setter
    def snippet_data(self, value):
        self._snippet_data = value

    def _init_ui(self):
        self.layout = QtWidgets.QHBoxLayout(self)

        self.snippet_viewer = snippet_viewer.SnippetViewer(self)
        self.snippet_editor = snippet_editor.SnippetEditor(self)
        self.vex_editor = self.snippet_editor.editor
        self.table = self.snippet_viewer.table

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.snippet_viewer)
        self.splitter.addWidget(self.snippet_editor)

        self.table.selectionModel().selectionChanged.connect(
            self.change_table_selection)
        self.table.model.dataChanged.connect(self.label_renamed)
        self.snippet_viewer.add_btn.clicked.connect(self.begin_new_snippet)
        self.snippet_editor.save_btn.clicked.connect(self.save_snippet)
        self.snippet_editor.cancel_btn.clicked.connect(self.discard_snippet)
        self.layout.addWidget(self.splitter)

        # # tmp Load validate.txt into the editor for demo purposes
        # with open('C:/Users/dchow/Documents/_GitHub/Vex_Snippet_Library/vex_syntax/validate.txt', 'r') as txt:
        #     x = txt.read()
        #     self.vex_editor.setPlainText(x)

    def load_snippets(self):
        snippets = []
        for (dirpath, dirnames, filenames) in os.walk(self.json_path):
            for file in filenames:
                head, tail = os.path.splitext(file)
                if tail == '.json':
                    snippets.append(os.path.join(dirpath, file))
        for file in snippets:
            with open(file, 'r') as f:
                item_dict = json.load(f)
                self.table.add_item(item_dict)

    def begin_new_snippet(self):
        if self.editing:
            # todo: unsaved changes prompt
            # todo: handle create while editing ( probably disable btns )
            return None

        new_name, ok = QtWidgets.QInputDialog().getText(
            self,
            'Create',
            'Snippet Name:',
            QtWidgets.QLineEdit.Normal,
            'NewSnippet')

        if ok and new_name:
            self.snippet_name = new_name
            self.creating = True
            self.snippet_viewer.setEnabled(False)
            self.snippet_editor.edit_btn.animateClick()
            self.vex_editor.setPlainText('')

    def save_snippet(self):
        if self.creating:
            new_snippet = self.build_snippet_dict()
            self.write_snippet(new_snippet)
            self.table.add_item(self.snippet_data)
            self.snippet_viewer.setEnabled(True)
            self.creating = False

            # select new snippet in table
            rows = self.table.model.rowCount()
            for row in range(rows):
                idx = self.table.model.index(rows-1, 0)
                data = self.table.model.data(idx, QtCore.Qt.DisplayRole)
                if data == self.snippet_name:
                    self.table.selectionModel().setCurrentIndex(
                        idx, QtCore.QItemSelectionModel.Select)
                    break

    def discard_snippet(self):
        if self.creating:
            self.creating = False
            self.snippet_viewer.setEnabled(True)
            if self.prev_idx:
                self.table.selectionModel().setCurrentIndex(
                    self.prev_idx, QtCore.QItemSelectionModel.Select)

    def build_snippet_dict(self):
        snippet_context = self.snippet_editor.combo.currentText()
        snippet_text = self.vex_editor.toPlainText()
        new_dict = {
            'label': self.snippet_name,
            'context': snippet_context,
            'data': snippet_text
        }
        return new_dict

    def write_snippet(self, snippet_dict):
        new_json = os.path.join(
            self.json_path, '{}.json'.format(self.snippet_name))
        with open(new_json, 'w+') as f:
            json.dump(snippet_dict, f, indent=4)
        self.snippet_data = snippet_dict

    def change_table_selection(self):
        # todo: popup if editing
        # cache selected table item
        if self.table.selectionModel().hasSelection():
            x = self.table.selectionModel().selectedIndexes()
            if not x:
                self.prev_idx = None
                return
            self.prev_idx = self.table.selectionModel().selectedIndexes()[0]
            self.snippet_data = self.prev_idx.data(role=QtCore.Qt.UserRole)
            self.snippet_name = self.snippet_data['label']
            self.vex_editor.setPlainText(self.snippet_data['data'])
            combo_index = self.snippet_editor.combo.findText(
                self.snippet_data['context'])
            self.snippet_editor.combo.setCurrentIndex(combo_index)
        else:
            self.prev_idx = None

    def label_renamed(self, top_left, bottom_right):
        data = top_left.data(role=QtCore.Qt.UserRole)
        src = os.path.join(self.json_path, '{}.json'.format(self.snippet_name))
        dst = os.path.join(self.json_path, '{}.json'.format(data['label']))
        os.rename(src, dst)
        with open(dst, 'w+') as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = VexSnippetLibrary()
    editor.setGeometry(355, 225, 800, 800)
    editor.show()

    app.exec_()

