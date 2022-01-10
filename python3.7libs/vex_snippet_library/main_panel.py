import os

import sys

import string

import json

import logging

from PySide2 import QtWidgets, QtCore

# tmp
logging.basicConfig(level=logging.DEBUG)
sys.path.append('C:/Users/dchow/Documents/_GitHub/Vex_Snippet_Library/python3.7libs')
# end tmp

from vex_snippet_library.widgets import snippet_editor

from vex_snippet_library.widgets import snippet_viewer

from vex_snippet_library.widgets import button_table


class VexSnippetLibrary(QtWidgets.QWidget):
    def __init__(self):
        super(VexSnippetLibrary, self).__init__()
        self._creating = False
        self._editing = False
        self.snippet = None
        self._snippet_data = {}
        self.cached_index = None
        self.cached_label = ''
        self.new_label = ''
        self.root = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
        self.json_path = os.path.join(self.root, 'json')
        self._init_ui()

    def _init_ui(self):
        self.layout = QtWidgets.QHBoxLayout(self)

        self.snippet_viewer = snippet_viewer.SnippetViewer(self)
        self.snippet_editor = snippet_editor.SnippetEditor(self)
        self.vex_editor = self.snippet_editor.editor
        self.table = self.snippet_viewer.table
        self.model = self.table.model

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.snippet_viewer)
        self.splitter.addWidget(self.snippet_editor)
        self.splitter.setStretchFactor(1, 3)

        self.snippet_viewer.add_btn.clicked.connect(self.begin_new_snippet)
        self.snippet_viewer.del_btn.clicked.connect(self.delete_snippet)
        self.snippet_editor.edit_btn.clicked.connect(self.edit_snippet)
        self.snippet_editor.save_btn.clicked.connect(self.save_snippet)
        self.snippet_editor.cancel_btn.clicked.connect(self.discard_snippet)
        self.model.dataChanged.connect(self.label_renamed)
        self.table.selectionModel().selectionChanged.connect(
            self.update_selection)

        self.layout.addWidget(self.splitter)
        self.load_snippets()

        # initial selection
        idx = self.table.model.index(0, 0)
        self.snippet = idx.data(role=QtCore.Qt.UserRole)
        self.table.setCurrentIndex(idx)

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
                self.table.add_item(button_table.Snippet(item_dict))

    def begin_new_snippet(self):
        self.table.blockSignals(True)
        new_label, ok = QtWidgets.QInputDialog().getText(
            self,
            'Create',
            'Snippet Name:',
            QtWidgets.QLineEdit.Normal,
            'NewSnippet')
        self.table.blockSignals(False)

        if ok and new_label:
            self._creating = True
            self.new_label = self.model.build_unique_label(new_label)
            self.table.selectionModel().reset()
            self.snippet_editor.edit_btn.blockSignals(False)
            self.snippet_editor.edit_btn.animateClick()
            self.vex_editor.setPlainText('')

    def save_snippet(self):
        new_snippet = self.build_new_snippet()
        self.write_snippet(new_snippet)
        self.snippet_viewer.setEnabled(True)

        if self._editing:
            snippet = self.model.data(self.cached_index, QtCore.Qt.UserRole)
            snippet.data = self.vex_editor.toPlainText().strip() + '\n'
            self.model.setData(self.cached_index, snippet, QtCore.Qt.UserRole)
            self.vex_editor.setPlainText(snippet.data)
        if self._creating:
            self.table.add_item(new_snippet)
            rows = self.model.rowCount()
            model_idx = self.model.index(rows - 1, 0)
            filter_idx = self.table.filter.mapFromSource(model_idx)
            if not self.snippet:
                self.snippet = self.model.data(model_idx, QtCore.Qt.UserRole)
            self.table.setCurrentIndex(filter_idx)

        self._creating = False
        self._editing = False

    def edit_snippet(self):
        if not self._creating:
            if self.table.selectionModel().hasSelection():
                self._editing = True
                self.snippet_viewer.setEnabled(False)
        else:
            self.snippet_viewer.setEnabled(False)

    def discard_snippet(self):
        if self._creating:
            self.table.blockSignals(False)
        self.snippet_viewer.setEnabled(True)
        self._creating = False
        self._editing = False
        if self.cached_index:
            self.table.setCurrentIndex(self.cached_index)

    def build_new_snippet(self):
        snippet_context = self.snippet_editor.combo.currentText()
        snippet_text = self.vex_editor.toPlainText().strip() + '\n'
        snippet_label = self.snippet.label if self.snippet else ''
        if self._creating:
            snippet_label = self.new_label
        new_dict = {
            'label': snippet_label,
            'context': snippet_context,
            'data': snippet_text
        }
        return button_table.Snippet(new_dict)

    def write_snippet(self, snippet):
        logging.debug('Writing snippet: {}'.format(snippet.to_dict()))
        new_json = os.path.join(
            self.json_path, '{}.json'.format(snippet.label))
        with open(new_json, 'w+') as f:
            json.dump(snippet.to_dict(), f, indent=4)

    def delete_snippet(self):
        logging.debug('Delete Snippet Callback')
        sel = self.table.selectionModel().selectedIndexes()
        if sel:
            filter_idx = sel[0]
            model_idx = self.table.filter.mapToSource(filter_idx)
            data = self.model.data(model_idx, QtCore.Qt.DisplayRole)
            to_del = os.path.join(self.json_path, '{}.json'.format(data))
            if os.path.isfile(to_del):
                os.remove(to_del)
                self.table.remove_item()

    def update_selection(self):
        logging.debug('Selection Update Callback')
        sel = self.table.selectionModel().selectedIndexes()
        if sel:
            self.snippet_editor.edit_btn.blockSignals(False)
            self.cached_index = sel[0]
            self.cached_label = self.snippet.label
            self.snippet = self.cached_index.data(role=QtCore.Qt.UserRole)
            self.vex_editor.setPlainText(self.snippet.data)
            combo_index = self.snippet_editor.combo.findText(
                self.snippet.context)
            self.snippet_editor.combo.setCurrentIndex(combo_index)
            logging.debug('Previous: {}'.format(self.cached_label))
            logging.debug('Current: {}'.format(self.snippet.label))
        else:
            self.cached_index = None
            self.snippet_editor.edit_btn.blockSignals(True)
            self.vex_editor.setPlainText('')
        self.snippet_viewer.add_btn.setFocus()  # table select hotfix

    def label_renamed(self, top_left, bottom_right):
        logging.debug('Renamed Callback')
        logging.debug('source: {}'.format(self.snippet.label))
        logging.debug('dest: {}'.format(self.snippet.new_name))

        snippet = top_left.data(role=QtCore.Qt.UserRole)
        src = os.path.join(self.json_path, '{}.json'.format(snippet.label))
        dst = os.path.join(self.json_path, '{}.json'.format(snippet.new_name))
        os.rename(src, dst)

        self.model.beginResetModel()
        self.table.blockSignals(True)
        snippet.label = snippet.new_name
        self.model.endResetModel()
        self.table.blockSignals(False)

        self.write_snippet(snippet)
        filter_idx = self.table.filter.mapFromSource(top_left)
        self.table.setCurrentIndex(filter_idx)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = VexSnippetLibrary()
    editor.setGeometry(355, 225, 800, 800)
    editor.show()

    app.exec_()
