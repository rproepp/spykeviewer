from PyQt4.QtGui import (QDialog, QLabel, QComboBox, QDialogButtonBox,
                         QGridLayout, QLineEdit, QMessageBox, QCheckBox,
                         QFont)
from PyQt4.QtCore import Qt, SIGNAL

from spyderlib.widgets.sourcecode.codeeditor import CodeEditor

class FilterDialog(QDialog):
    """ A dialog for editing filters
    """

    def __init__(self, groups, type=None, group=None, name=None, code=None, on_exception=False, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi()
        self.groups = groups

        if type:
            index = self.filterTypeComboBox.findText(type)
            if index >= 0:
                self.filterTypeComboBox.setCurrentIndex(index)

        self.populate_groups()
        if group:
            index = self.filterGroupComboBox.findText(group)
            if index >= 0:
                self.filterGroupComboBox.setCurrentIndex(index)

        if name:
            self.nameLineEdit.setText(name)
        if code:
            self.editor.set_text('\n'.join(code))
        if name and code and type:
            self.filterTypeComboBox.setEnabled(False)

        self.onExceptionCheckBox.setChecked(on_exception)

    def populate_groups(self):
        self.filterGroupComboBox.clear()
        self.filterGroupComboBox.addItem('')
        for g in sorted(self.groups[self.filterTypeComboBox.currentText()]):
            self.filterGroupComboBox.addItem(g)

    def setupUi(self):
        self.setWindowTitle('Edit filter')
        #self.resize(400, 300)

        self.signatureLabel = QLabel(self)
        self.signatureLabel.setText('def filter(block):')

        font = QFont('Some font that does not exist')
        font.setStyleHint(font.TypeWriter, font.PreferDefault)
        self.editor = CodeEditor()
        self.editor.setup_editor(linenumbers=False, language='py',
            scrollflagarea=False, codecompletion_enter=True, font=font,
            highlight_current_line=False, occurence_highlighting=False)
        self.editor.set_text('return True')
        self.editor.setCursor(Qt.IBeamCursor)

        self.onExceptionCheckBox = QCheckBox(self)
        self.onExceptionCheckBox.setText('True on exception')
        self.onExceptionCheckBox.setToolTip('Determines if the filter will be admit items if there is an exception during its execution')

        self.filterTypeComboBox = QComboBox(self)
        self.filterTypeComboBox.addItem('Block')
        self.filterTypeComboBox.addItem('Segment')
        self.filterTypeComboBox.addItem('Recording Channel Group')
        self.filterTypeComboBox.addItem('Recording Channel')
        self.filterTypeComboBox.addItem('Unit')

        self.filterGroupComboBox = QComboBox(self)

        self.nameLineEdit = QLineEdit()

        self.dialogButtonBox = QDialogButtonBox(self)
        self.dialogButtonBox.setAutoFillBackground(False)
        self.dialogButtonBox.setOrientation(Qt.Horizontal)
        self.dialogButtonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.dialogButtonBox.setCenterButtons(True)

        gridLayout = QGridLayout(self)
        gridLayout.addWidget(self.signatureLabel, 0, 0, 1, 2)
        gridLayout.addWidget(self.editor, 1, 0, 1, 2)
        gridLayout.addWidget(self.onExceptionCheckBox, 2,0, 1, 2)
        gridLayout.addWidget(QLabel('Type:', self), 3, 0)
        gridLayout.addWidget(self.filterTypeComboBox, 3, 1)
        gridLayout.addWidget(QLabel('Group:', self), 4, 0)
        gridLayout.addWidget(self.filterGroupComboBox, 4, 1)
        gridLayout.addWidget(QLabel('Name:', self), 5, 0)
        gridLayout.addWidget(self.nameLineEdit, 5, 1)
        gridLayout.addWidget(self.dialogButtonBox, 6, 0, 1, 2)

        self.connect(self.dialogButtonBox, SIGNAL('accepted()'), self.accept)
        self.connect(self.dialogButtonBox, SIGNAL('rejected()'), self.reject)
        self.connect(self.filterTypeComboBox, SIGNAL('currentIndexChanged(int)'), self.on_filterTypeComboBox_currentIndexChanged)

    def name(self):
        return self.nameLineEdit.text()

    def code(self):
        return [self.editor.get_text_line(l) for l in xrange(self.editor.get_line_count())]

    def type(self):
        return self.filterTypeComboBox.currentText()

    def group(self):
        if self.filterGroupComboBox.currentText() == '':
            return None
        return self.filterGroupComboBox.currentText()

    def on_exception(self):
        return self.onExceptionCheckBox.isChecked()

    def code_errors(self):
        code = self.signatureLabel.text() + '\n\t'
        code += '\n\t'.join(self.code())
        try:
            compile(code, '<filter>', 'exec')
        except SyntaxError as e:
            return e.msg + ' (Line %d)' % (e.lineno - 1)
        return None

    def on_filterTypeComboBox_currentIndexChanged(self, index):
        if index == 0:
            self.signatureLabel.setText('def filter(block):')
        elif index == 1:
            self.signatureLabel.setText('def filter(segment):')
        elif index == 2:
            self.signatureLabel.setText('def filter(rcg):')
        elif index == 3:
            self.signatureLabel.setText('def filter(rc):')
        elif index == 4:
            self.signatureLabel.setText('def filter(unit):')
        self.populate_groups()

    #noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    def accept(self):
        if len(self.nameLineEdit.text()) < 1:
            QMessageBox.critical(self, 'Error saving filter', 'Please provide a name for the filter.')
            return
        if '"' in self.nameLineEdit.text():
            QMessageBox.critical(self, 'Error saving filter', 'You cannot use " in the name of a filter.')
            return
        err = self.code_errors()
        if err:
            QMessageBox.critical(self, 'Error saving filter', 'Compile error:\n' + err)
            return

        QDialog.accept(self)