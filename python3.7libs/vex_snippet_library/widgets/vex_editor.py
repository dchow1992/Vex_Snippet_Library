import os

import re

import logging

from PySide2 import QtWidgets, QtCore, QtGui

from . import vex_highlighter

logger = logging.getLogger('vex_snippet_library.main_panel.vex_editor')


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.myeditor = editor
        self.bg_color = QtGui.QColor(43, 43, 43)
        self.line_color = QtGui.QColor(75, 75, 75)
        self.num_color = QtGui.QColor(200, 200, 200)

    def sizeHint(self):
        return QtCore.Qt.Qsize(self.editor._line_num_area_width(), 0)

    def paintEvent(self, event):
        self.myeditor.line_num_area_paint(event)

    def disable(self):
        self.bg_color = QtGui.QColor(83, 83, 83)
        self.line_color = QtGui.QColor(105, 105, 105)
        self.num_color = QtGui.QColor(200, 200, 200)

    def enable(self):
        self.bg_color = QtGui.QColor(43, 43, 43)
        self.line_color = QtGui.QColor(75, 75, 75)
        self.num_color = QtGui.QColor(200, 200, 200)


class VexEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super(VexEditor, self).__init__(parent)
        self.line_num_area = LineNumberArea(self)
        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'),
                     self._update_line_num_width)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect,int)'),
                     self._update_line_num_area)
        self._update_line_num_width(0)
        self._init_ui()

    def _init_ui(self):
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.installEventFilter(self)
        self.highlighter = vex_highlighter.VexHighlighter(
            self.document())
        root = os.path.abspath(os.path.join(__file__, '..', '..', '..', '..'))
        fonts = os.path.join(root, 'resources', 'fonts')
        QtGui.QFontDatabase.addApplicationFont(
            os.path.join(fonts, 'SourceCodePro-Regular.ttf'))

        font = QtGui.QFont('Source Code Pro')
        self.setFont(font)
        self.enable_editor()

    def eventFilter(self, widget, event):
        """Custom support for editor behavior"""
        if (event.type() == QtCore.QEvent.KeyPress and widget is self):
            key = event.key()
            # tabs to spaces
            if key == QtCore.Qt.Key_Tab:
                cursor = self.textCursor()
                if cursor.hasSelection():
                    lines = self._lines_from_sel(cursor)
                    cursor.beginEditBlock()
                    for line in lines:
                        doc = self.document()
                        get_block = doc.findBlockByLineNumber(line)
                        cursor = QtGui.QTextCursor(get_block)
                        self.setTextCursor(cursor)
                        self.insertPlainText('    ')
                    cursor.endEditBlock()
                    self._select_lines(lines)
                else:
                    self.insertPlainText('    ')
                return True

            # shift tab
            if key == QtCore.Qt.Key_Backtab:
                cursor = self.textCursor()
                if cursor.hasSelection():
                    lines = self._lines_from_sel(cursor)
                    cursor.beginEditBlock()
                    for line in lines:
                        doc = self.document()
                        get_block = doc.findBlockByLineNumber(line)
                        cursor = QtGui.QTextCursor(get_block)
                        self._unindent_line(cursor)
                    cursor.endEditBlock()
                    self._select_lines(lines)
                    return True
                else:
                    self._unindent_line(cursor)
                    return True

            # enter indent level
            if key == QtCore.Qt.Key_Return:
                cursor = self.textCursor()
                tmp = self.textCursor()
                pos = tmp.position()
                tmp.clearSelection()
                tmp.movePosition(QtGui.QTextCursor.EndOfLine,
                                 QtGui.QTextCursor.MoveAnchor)
                tmp.movePosition(QtGui.QTextCursor.StartOfLine,
                                 QtGui.QTextCursor.KeepAnchor)
                line_txt = str(tmp.selectedText()).replace('\u2029', '\n')
                leading_whitespace = len(line_txt) - len(line_txt.lstrip())
                x = 4
                indent_level = round(leading_whitespace / x)
                out = '\n'
                if leading_whitespace:
                    for i in range(indent_level):
                        out += '    '
                cursor.insertText(out)
                return True

        return QtWidgets.QWidget.eventFilter(self, widget, event)

    def disable_editor(self):
        self.setReadOnly(True)
        self.line_num_area.disable()
        self.setStyleSheet("QPlainTextEdit {background-color:#404040;}")

    def enable_editor(self):
        self.setReadOnly(False)
        self.line_num_area.enable()
        self.setStyleSheet("QPlainTextEdit {background-color:#131313;}")

    def _unindent_line(self, cursor):
        """Unindent current line at cursor"""
        pos = cursor.position()
        cursor.clearSelection()
        cursor.movePosition(QtGui.QTextCursor.EndOfLine,
                            QtGui.QTextCursor.MoveAnchor)
        cursor.movePosition(QtGui.QTextCursor.StartOfLine,
                            QtGui.QTextCursor.KeepAnchor)

        line_txt = str(cursor.selectedText()).replace('\u2029', '\n')
        leading_whitespace = len(line_txt) - len(line_txt.lstrip())
        cursor.insertText(line_txt[min(3, leading_whitespace):])
        cursor.setPosition(pos - min(3, leading_whitespace))

    def _select_lines(self, lines):
        """Selects full lines, expects lines to be a generator"""
        doc = self.document()
        start_block = doc.findBlockByLineNumber(lines[0])
        cursor = QtGui.QTextCursor(start_block)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine,
                            QtGui.QTextCursor.KeepAnchor)
        for x in lines[1:]:
            cursor.movePosition(QtGui.QTextCursor.NextBlock,
                                QtGui.QTextCursor.KeepAnchor)
            cursor.movePosition(QtGui.QTextCursor.EndOfBlock,
                                QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def _lines_from_sel(self, cursor):
        """Return selected lines as a generator object"""
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        tmp = self.textCursor()
        tmp.setPosition(sel_start)
        start_line = tmp.blockNumber()
        tmp.setPosition(sel_end)
        end_line = tmp.blockNumber()
        return range(start_line, end_line + 1)

    def _line_num_area_width(self):
        digits = 1
        # count = max(1, self.blockCount())
        # while count >= 10:
        #     count /= 10
        #     digits += 1
        digits = 2
        space = 18 + self.fontMetrics().width('9') * digits
        return space

    def _update_line_num_width(self, _):
        self.setViewportMargins(self._line_num_area_width(), 0, 0, 0)

    def _update_line_num_area(self, rect, dy):

        if dy:
            self.line_num_area.scroll(0, dy)
        else:
            self.line_num_area.update(
                0, rect.y(), self.line_num_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._update_line_num_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_num_area.setGeometry(
            QtCore.QRect(
                cr.left(), cr.top(), self._line_num_area_width(), cr.height()))

    def line_num_area_paint(self, event):
        my_painter = QtGui.QPainter(self.line_num_area)

        my_painter.fillRect(event.rect(), self.line_num_area.bg_color)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                if block == self.textCursor().block():
                    line_rect = QtCore.QRect(
                        0, top, self.line_num_area.width(), height)
                    my_painter.fillRect(
                        line_rect, self.line_num_area.line_color)
                my_painter.setPen(self.line_num_area.num_color)
                my_painter.drawText(
                    0, top, self.line_num_area.width(),
                    height, QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
