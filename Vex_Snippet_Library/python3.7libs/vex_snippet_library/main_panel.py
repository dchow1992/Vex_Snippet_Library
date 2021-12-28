import hou

from PySide2 import QtWidgets

from vex_snippet_library.compound_widgets import snippet_item

from importlib import reload
reload(snippet_item)


class VexSnippetLibrary(QtWidgets.QWidget):
    def __init__(self):
        super(VexSnippetLibrary, self).__init__()
        self.layout = hou.qt.GridLayout()

        self.label = snippet_item.SnippetItem()
        self.label2 = snippet_item.SnippetItem()

        self.setLayout(self.layout)
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.label2, 1, 0)
