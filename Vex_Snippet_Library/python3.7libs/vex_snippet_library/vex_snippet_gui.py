from PySide2 import QtWidgets

class VexSnippetLibrary(QtWidgets.QWidget):
    def __init__(self):
        super(VexSnippetLibrary, self).__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel('Hello orld!')

        self.setLayout(self.layout)
        self.layout.addWidget(self.label)