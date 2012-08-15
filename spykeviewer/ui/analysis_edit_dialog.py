from PyQt4.QtGui import (QDialog, QFileDialog, QDialogButtonBox,
                         QGridLayout, QMessageBox, QFont)
from PyQt4.QtCore import Qt

from spyderlib.widgets.sourcecode.codeeditor import CodeEditor

class AnalysisEditDialog(QDialog):
    """ A dialog for editing filters
    """

    template_code = \
"""from spykeviewer.plugin_framework.analysis_plugin import AnalysisPlugin

class SamplePlugin(AnalysisPlugin):
    def get_name(self):
        return 'New plugin'

    def start(self, current, selections):
        print 'Plugin started.'
"""

    def __init__(self, filename, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi()
        self.filename = filename
        if filename.endswith('py'):
            self.editor.set_text_from_file(filename)
        else:
            self.editor.set_text(self.template_code)

    def populate_groups(self):
        self.filterGroupComboBox.clear()
        self.filterGroupComboBox.addItem('')
        for g in sorted(self.groups[self.filterTypeComboBox.currentText()]):
            self.filterGroupComboBox.addItem(g)

    def setupUi(self):
        self.setWindowTitle('Edit analysis')
        self.resize(600, 700)

        font = QFont('Some font that does not exist')
        font.setStyleHint(font.TypeWriter, font.PreferDefault)
        self.editor = CodeEditor()
        self.editor.setup_editor(linenumbers=True, language='py',
            scrollflagarea=False, codecompletion_enter=True,
            tab_mode=False, edge_line=False, font=font,
            codecompletion_auto=True, go_to_definition=True,
            codecompletion_single=True)
        self.editor.setCursor(Qt.IBeamCursor)
        self.editor.horizontalScrollBar().setCursor(Qt.ArrowCursor)
        self.editor.verticalScrollBar().setCursor(Qt.ArrowCursor)

        self.dialogButtonBox = QDialogButtonBox(self)
        self.dialogButtonBox.setAutoFillBackground(False)
        self.dialogButtonBox.setOrientation(Qt.Horizontal)
        self.dialogButtonBox.setStandardButtons(
            QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        self.dialogButtonBox.setCenterButtons(True)

        gridLayout = QGridLayout(self)
        gridLayout.addWidget(self.editor, 0, 0)
        gridLayout.addWidget(self.dialogButtonBox, 1, 0)

        self.dialogButtonBox.rejected.connect(self.reject)
        self.dialogButtonBox.clicked.connect(self.button_pressed)

    def code(self):
        return [self.editor.get_text_line(l)
                for l in xrange(self.editor.get_line_count())]

    def code_has_errors(self):
        code = '\n'.join(self.code())
        try:
            compile(code, '<filter>', 'exec')
        except SyntaxError as e:
            return e.msg + ' (Line %d)' % (e.lineno)
        return None

    #noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    def button_pressed(self, button):
        if button == self.dialogButtonBox.button(QDialogButtonBox.Save):
            if not self.filename.endswith('py'):
                d = QFileDialog(self, 'Choose where to save selection',
                    self.filename)
                d.setAcceptMode(QFileDialog.AcceptSave)
                d.setNameFilter("Python files (*.py)")
                d.setDefaultSuffix('py')
                if d.exec_():
                    self.filename = str(d.selectedFiles()[0])
                else:
                    return
            #else:
            #    if QMessageBox.question(self, 'Warning',
            #        'Do you really want to overwrite the existing file?',
            #        QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            #        return

            err = self.code_has_errors()
            if err:
                QMessageBox.critical(self, 'Error saving analysis',
                    'Compile error:\n' + err)
                return

            f = open(self.filename, 'w')
            f.write('\n'.join(self.code()))
            self.accept()