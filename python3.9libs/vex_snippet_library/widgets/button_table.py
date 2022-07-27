import os

import re

import string

import logging

from PySide2 import QtCore, QtGui, QtWidgets

logger = logging.getLogger('vex_snippet_library.main_panel.button_table')


class ButtonDelegate(QtWidgets.QStyledItemDelegate):
    copyRequest = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if isinstance(self.parent(), QtWidgets.QAbstractItemView):
            self.parent().openPersistentEditor(index)
        super(ButtonDelegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QPushButton(parent)
        editor.setToolTip('Copy Snippet')
        root = os.path.abspath(
            os.path.join(os.path.abspath(__file__), '..', '..', '..', '..'))
        icons = os.path.join(root, 'resources', 'icons')
        icon = QtGui.QIcon(QtGui.QPixmap(os.path.join(icons, 'copy.png')))
        editor.setIcon(icon)

        table = self.parent()
        row_height = table.verticalHeader().defaultSectionSize()
        editor.setIconSize(QtCore.QSize(row_height/1.7, row_height/1.7))
        editor.setFixedSize(row_height/1.1, row_height/1.1)
        editor.clicked.connect(lambda: self.copyRequest.emit(index))
        return editor

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        pass

    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        rect.setX(rect.x() + rect.width()/2-editor.size().width()/2)
        rect.setY(rect.y() + rect.height()/2-editor.size().height()/2)
        editor.setGeometry(rect)


class SnippetModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(SnippetModel, self).__init__()
        self.table_data = []
        self.n_columns = 2

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.table_data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.n_columns

    def flags(self, index):
        col = index.column()
        if col == 0:
            return (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable |
                    QtCore.Qt.ItemIsEditable)
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        item = self.table_data[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 1:  # button column
                return None
            return item.label
        elif role == QtCore.Qt.UserRole:
            return item
        elif role == QtCore.Qt.EditRole or role == QtCore.Qt.ToolTipRole:
            return item.label
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                img = {
                    'Detail': 'info.svg',
                    'Points': 'filter_color_blue.svg',
                    'Primitives': 'display_primitive_normals.svg',
                    'Vertices': 'filter_color_purple.svg'
                }
                root = os.path.abspath(
                    os.path.join(__file__, '..', '..', '..', '..'))
                icons = os.path.join(root, 'resources', 'icons')
                path = os.path.join(icons, img[item.context])
                pxmap = QtGui.QPixmap(path)
                icon = QtGui.QIcon(pxmap)
                return icon

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            item = self.table_data[index.row()]
            if role == QtCore.Qt.EditRole:
                is_valid = re.match(r'^(?=.*[^\W_])[\w ]*$', value)
                if not is_valid:
                    return False
                if item.label == value:
                    return True
                item.new_name = self.build_unique_label(value)
                self.table_data[index.row()] = item
                self.dataChanged.emit(index, index, [QtCore.Qt.EditRole])
                return True
            elif role == QtCore.Qt.UserRole:
                self.table_data[index.row()] = value
                # self.dataChanged.emit(index, index, [QtCore.Qt.DecorationRole])
                return True
        else:
            return False

    def removeRows(self, pos, rows=1):
        self.beginRemoveRows(QtCore.QModelIndex(), pos, pos + rows - 1)
        self.table_data.pop(pos)
        self.endRemoveRows()
        return True

    def insertRows(self, data):
        n = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), n, n)
        data.label = self.build_unique_label(data.label)
        self.table_data.append(data)
        self.endInsertRows()

    def build_unique_label(self, input_str):
        new_name = input_str.strip().replace(' ', '_')
        data = self.table_data
        labels = [x.label for x in data]
        while(new_name in labels):
            head = new_name.rstrip(string.digits)
            tail = new_name.replace(head, '')
            digit = int(tail) + 1 if tail else 1
            new_name = '{}{}'.format(head, digit)
        return new_name


class SnippetProxyModel(QtCore.QSortFilterProxyModel):
    def __init(self, parent):
        super(SnippetProxyModel, self).__init__(parent)

    def lessThan(self, left, right):
        left_data = self.sourceModel().data(left, role=QtCore.Qt.DisplayRole)
        right_data = self.sourceModel().data(right, role=QtCore.Qt.DisplayRole)
        input_set = set([left_data, right_data])
        sorted_set = self.sorted_nicely(input_set)
        return right_data == sorted_set[0]

    def sorted_nicely(self, input_set):
        """ Sort the given iterable in the way that humans expect."""
        conv = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [conv(c) for c in re.split('([0-9]+)', key)]
        return sorted(input_set, key=alphanum_key)


class ButtonTable(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(ButtonTable, self).__init__(parent)
        self.model = SnippetModel()
        self.setModel(self.model)

        self.filter = SnippetProxyModel(self)
        self.filter.setSourceModel(self.model)
        self.filter.setFilterKeyColumn(0)
        self.setModel(self.filter)

        btn_delegate = ButtonDelegate(self)
        btn_delegate.copyRequest.connect(self.btn_callback)
        self.setItemDelegateForColumn(1, btn_delegate)
        self.model.rowsInserted.connect(self.scrollToBottom)

        v_header = self.verticalHeader()
        v_header.hide()
        h_header = self.horizontalHeader()
        h_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        h_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        h_header.resizeSection(1, 36)
        h_header.hide()

        sel = QtWidgets.QTableView.SingleSelection
        beh = QtWidgets.QTableView.SelectRows

        self.setSelectionMode(sel)
        self.setSelectionBehavior(beh)
        self.setSortingEnabled(True)
        self.setShowGrid(False)

    def mousePressEvent(self, event):
        pt = QtCore.QPoint(1, event.pos().y())
        if self.indexAt(pt).row() == -1:  # deselect on bg click
            self.selectionModel().clear()
            self.parent().add_btn.setFocus()  # focus fix
        else:
            index = self.indexAt(event.pos())
            if index.column() == 0:  # snippet select
                super(ButtonTable, self).mousePressEvent(event)
            elif index.column() == 1:  # column behind button
                self.parent().add_btn.setFocus()  # focus fix

    def add_item(self, snippet):
        self.model.beginResetModel()
        self.model.insertRows(snippet)
        self.model.endResetModel()

    def remove_item(self):
        self.model.beginResetModel()
        proxy_index = self.currentIndex()
        model_index = self.filter.mapToSource(proxy_index)
        r = model_index.row()
        self.model.removeRows(r)
        self.model.endResetModel()

    def btn_callback(self, index):
        model_index = self.filter.mapToSource(index)
        snippet = model_index.siblingAtColumn(1).data(role=QtCore.Qt.UserRole)

        logger.debug('Filter Index: {}'.format(index))
        logger.debug('Model Index: {}'.format(model_index))
        logger.debug('Copied Snippet: {}'.format(snippet.label))

        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(snippet.data, mode=cb.Clipboard)
        self.parent().add_btn.setFocus()  # focus fix
