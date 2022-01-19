import os

from zipfile import ZipFile

from PySide2 import QtGui, QtCore


class VexSyntaxUtilities():
    def __init__(self):
        self.package = os.path.abspath(
            os.path.join(__file__, '..', '..', '..', '..'))
        self.vex_dir = os.path.join(self.package, 'resources', 'vex_syntax')
        self.vex_data_types = ''
        self.vex_functions = ''
        self.vex_keywords = ''
        self.vex_macros = ''
        self.vex_comments = ''

    def load_vex_syntax(self):
        data_types_file = os.path.join(self.vex_dir, 'vex_data_types.txt')
        with open(data_types_file, 'r') as t:
            self.vex_data_types = '|'.join(t.read().splitlines())

        functions_file = os.path.join(self.vex_dir, 'vex_functions.txt')
        with open(functions_file, 'r') as t:
            self.vex_functions = '|'.join(t.read().splitlines())

        keywords_file = os.path.join(self.vex_dir, 'vex_keywords.txt')
        with open(keywords_file, 'r') as t:
            self.vex_keywords = '|'.join(t.read().splitlines())

        macros_file = os.path.join(self.vex_dir, 'vex_macros.txt')
        with open(macros_file, 'r') as t:
            self.vex_macros = '|'.join(t.read().splitlines())

        comments_file = os.path.join(self.vex_dir, 'vex_comments.txt')
        with open(comments_file, 'r') as t:
            self.vex_comments = '|'.join(t.read().splitlines())

    def verify_vex_syntax(self):
        if not os.path.isdir(self.vex_dir):
            os.makedirs(self.vex_dir)
            self.write_vex_function_list()

    def write_vex_function_list(self):
        hfs = os.path.abspath(os.environ['HFS'])
        zip_file = os.path.join(hfs, 'houdini', 'help', 'vex.zip')
        with ZipFile(zip_file, 'r') as zip_obj:
            list_of_files = zip_obj.namelist()
            vex_functions = []
            for x in list_of_files:
                if 'functions/' in x:
                    vex_functions.append(x.split('/')[-1].split('.txt')[0])
        textfile = os.path.join(self.vex_dir, 'vex_functions.txt')
        with open(textfile, 'w+') as t:
            for f in vex_functions:
                t.write('{}\n'.format(f))


class VexColors():
    def __init__(self):
        self.colors = {
            'default': QtGui.QTextCharFormat(),
            'data_types': QtGui.QTextCharFormat(),
            'functions': QtGui.QTextCharFormat(),
            'keywords': QtGui.QTextCharFormat(),
            'macros': QtGui.QTextCharFormat(),
            'comment': QtGui.QTextCharFormat(),
            'string_double': QtGui.QTextCharFormat(),
            'string_single': QtGui.QTextCharFormat(),
            'attributes': QtGui.QTextCharFormat()
            }
        for key, value in self.colors.items():
            value.setFontWeight(QtGui.QFont.Bold)

        self.colors['default'].setForeground(QtGui.QBrush(
            QtGui.QColor(255, 255, 255)))

        self.colors['data_types'].setForeground(QtGui.QBrush(
            QtGui.QColor(255, 128, 255)))

        self.colors['functions'].setForeground(QtGui.QBrush(
            QtGui.QColor(115, 230, 230)))

        self.colors['keywords'].setForeground(QtGui.QBrush(
            QtGui.QColor(237, 119, 237)))

        self.colors['macros'].setForeground(QtGui.QBrush(
            QtGui.QColor(207, 162, 104)))

        self.colors['attributes'].setForeground(QtGui.QBrush(
            QtGui.QColor(207, 162, 104)))

        self.colors['comment'].setForeground(QtGui.QBrush(
            QtGui.QColor(250, 250, 125)))

        self.colors['string_double'].setForeground(QtGui.QBrush(
            QtGui.QColor(102, 204, 102)))

        self.colors['string_single'].setForeground(QtGui.QBrush(
            QtGui.QColor(102, 204, 102)))


class VexHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, *args, **kwargs):
        super(VexHighlighter, self).__init__(*args, **kwargs)
        self.utils = VexSyntaxUtilities()
        self.utils.load_vex_syntax()
        self.colors = VexColors().colors
        self.patterns = {
            'data_types': r'\b({})\b(?=\s|$)'.format(self.utils.vex_data_types),
            'functions': r'\b({})(?=\s|[(]|$)'.format(self.utils.vex_functions),
            'keywords': r'\b({})(?=\s|[(]|$)'.format(self.utils.vex_keywords),
            'attributes': r'((?<!\w)[A-Za-z0-9]?)\@\w+',
            'string_double': r'"[^"\\]*(\\.[^"\\]*)*"',
            'string_single': r"'[^'\\]*(\\.[^'\\]*)*'",
            'macros': r'#[^\n]*',
            'comment': r'\/\/[^\n]*'
            }

    def highlightBlock(self, text):
        self.setFormat(0, len(text), self.colors['default'])
        for pattern, exp in self.patterns.items():
            expression = QtCore.QRegularExpression(self.patterns[pattern])
            index = expression.globalMatch(text, 0)
            while index.hasNext():
                match = index.next()
                start = match.capturedStart()
                end = match.capturedLength()
                self.setFormat(start, end, self.colors[pattern])

        # multi-line comments
        self.setCurrentBlockState(0)
        comment_start = QtCore.QRegExp(r'(\/\*)')
        comment_end = QtCore.QRegExp(r'(\*\/)')
        in_multiline = self.match_multiline(
            text, comment_start, comment_end, 1, self.colors['comment'])

    def match_multiline(self, text, start_pattern, end_pattern, in_state, style):
            """Do highlighting of multi-line strings. ``delimiter`` should be a
            ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
            ``in_state`` should be a unique integer to represent the corresponding
            state changes when inside those strings. Returns True if we're still
            inside a multi-line string when this function is finished.
            """
            # If inside triple-single quotes, start at 0
            if self.previousBlockState() == in_state:
                start = 0
                add = 0
            # Otherwise, look for the delimiter on this line
            else:
                start = start_pattern.indexIn(text)
                # Move past this match
                add = start_pattern.matchedLength()

            # As long as there's a delimiter match on this line...
            while start >= 0:
                # Look for the ending delimiter
                end = end_pattern.indexIn(text, start + add)
                # Ending delimiter on this line?
                if end >= add:
                    length = end - start + add + end_pattern.matchedLength()
                    self.setCurrentBlockState(0)
                # No; multi-line string
                else:
                    self.setCurrentBlockState(in_state)
                    length = len(text) - start + add
                # Apply formatting
                self.setFormat(start, length, style)
                # Look for the next match
                start = start_pattern.indexIn(text, start + length)

            # Return True if still inside a multi-line string, False otherwise
            if self.currentBlockState() == in_state:
                return True
            else:
                return False







