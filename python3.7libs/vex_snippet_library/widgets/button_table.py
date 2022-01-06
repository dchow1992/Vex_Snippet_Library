import os

import re

import string

from PySide2 import QtCore, QtGui, QtWidgets


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
        root = os.path.abspath(os.path.join(__file__, '..', '..', '..', '..'))
        icon = QtGui.QIcon(
            QtGui.QPixmap(os.path.join(root, 'icons', 'copy.png')))
        editor.setIcon(icon)
        editor.setIconSize(QtCore.QSize(18, 18))
        editor.setFixedSize(30, 30)
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
        # each element should be length 3 [[dict, x],]
        self.table_data = []
        self.n_columns = 2
        self.icons = os.path.abspath(
            os.path.join(__file__, '..', '..', '..', '..', 'icons'))

    def headerData(self, section, orientation, role):
        pass  # header will be turned off anyway

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
            return QtCore.Qt.ItemIsEnabled

    def data(self, index, role):
        if not index.isValid():
            return None
        item = self.table_data[index.row()][0]
        if role == QtCore.Qt.DisplayRole:
            # return None for icon / button column
            if index.column() != 0:
                return None
            return item['label']
        elif role == QtCore.Qt.UserRole:
            return item
        elif role == QtCore.Qt.EditRole:
            return item['label']
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                img = {
                    'Detail': 'info.svg',
                    'Points': 'filter_color_blue.svg',
                    'Primitives': 'display_primitive_normals.svg',
                    'Vertices': 'filter_color_purple.svg'
                }
                path = os.path.join(self.icons, img[item['context']])
                pxmap = QtGui.QPixmap(path)
                icon = QtGui.QIcon(pxmap)
                return icon

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            item = self.table_data[index.row()][index.column()]
            if role == QtCore.Qt.EditRole:
                if item['label'] == value:
                    return True
                item['label'] = self.build_unique_label(value)
                self.table_data[index.row()][index.column()] = item
                self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])
                return True
            elif role == QtCore.Qt.UserRole:
                self.table_data[index.row()][index.column()] = value
                return True
        else:
            return False

    def remove_row(self, index, rows=1):
        self.beginRemoveRows(QtCore.QModelIndex(), index, index + rows - 1)
        self.table_data.pop(index)
        self.endRemoveRows()
        return True

    def add_row(self, data):
        # for now we always add the item to the end
        n = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), n, n)
        data[0]['label'] = self.build_unique_label(data[0]['label'])
        self.table_data.append(data)
        self.endInsertRows()

    def build_unique_label(self, input_str):
        new_name = input_str.strip().replace(' ', '_')
        data = self.table_data
        labels = [x[0]['label'] for x in data]
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
    def __init__(self):
        super(ButtonTable, self).__init__()
        self.model = SnippetModel()
        self.setModel(self.model)

        v_header = self.verticalHeader()
        v_header.hide()
        h_header = self.horizontalHeader()
        h_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        h_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        h_header.resizeSection(1, 36)
        h_header.hide()

        self.filter = SnippetProxyModel(self)
        self.filter.setSourceModel(self.model)
        self.filter.setFilterKeyColumn(0)
        self.setModel(self.filter)

        btn_delegate = ButtonDelegate(self)
        btn_delegate.copyRequest.connect(self.btn_callback)
        self.setItemDelegateForColumn(1, btn_delegate)
        self.model.rowsInserted.connect(self.scrollToBottom)

        sel = QtWidgets.QAbstractItemView.SingleSelection
        self.setSelectionMode(sel)
        self.setSortingEnabled(True)
        self.setShowGrid(False)

    def add_item(self, item):
        # item expected to be a dictionary
        rows = self.model.rowCount()
        self.model.add_row([item, ''])

    def remove_item(self):
        r = self.currentIndex().row()
        self.model().remove_row(r)

    def btn_callback(self, index):
        # mapped = self.filter.mapToSource(index)
        mapped = index
        model_index = self.model.index(mapped.row(), mapped.column())
        snippet = model_index.siblingAtColumn(1).data(role=QtCore.Qt.UserRole)
        print(snippet['label'])

