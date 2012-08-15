from PyQt4.QtGui import (QDialog, QLabel, QComboBox, QDialogButtonBox,
                         QGridLayout, QLineEdit, QMessageBox, QCheckBox)
from PyQt4.QtCore import Qt, SIGNAL


class FilterGroupDialog(QDialog):
    """ A dialog for editing filters
    """

    def __init__(self, type=None, name=None, exclusive=False, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi()

        if type:
            index = self.filterTypeComboBox.findText(type)
            if index >= 0:
                self.filterTypeComboBox.setCurrentIndex(index)
        if name:
            self.nameLineEdit.setText(name)
            self.filterTypeComboBox.setEnabled(False)

        self.exclusiveCheckBox.setChecked(exclusive)

    def setupUi(self):
        self.setWindowTitle('Edit filter group')

        self.filterTypeComboBox = QComboBox(self)
        self.filterTypeComboBox.addItem('Block')
        self.filterTypeComboBox.addItem('Segment')
        self.filterTypeComboBox.addItem('Recording Channel Group')
        self.filterTypeComboBox.addItem('Recording Channel')
        self.filterTypeComboBox.addItem('Unit')

        self.nameLineEdit = QLineEdit()

        self.dialogButtonBox = QDialogButtonBox(self)
        self.dialogButtonBox.setAutoFillBackground(False)
        self.dialogButtonBox.setOrientation(Qt.Horizontal)
        self.dialogButtonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.dialogButtonBox.setCenterButtons(True)

        self.exclusiveCheckBox = QCheckBox(self)
        self.exclusiveCheckBox.setText('Only one filter can be active')
        self.exclusiveCheckBox.setToolTip('Determines if exactly one or an arbitrary number of filters in this group can be active at once')

        gridLayout = QGridLayout(self)
        gridLayout.addWidget(QLabel('Type:', self), 0, 0)
        gridLayout.addWidget(self.filterTypeComboBox, 0, 1)
        gridLayout.addWidget(QLabel('Name:', self), 1, 0)
        gridLayout.addWidget(self.nameLineEdit, 1, 1)
        gridLayout.addWidget(self.exclusiveCheckBox, 2, 0, 1, 2)
        gridLayout.addWidget(self.dialogButtonBox, 3, 0, 1, 2)

        self.connect(self.dialogButtonBox, SIGNAL('accepted()'), self.accept)
        self.connect(self.dialogButtonBox, SIGNAL('rejected()'), self.reject)

    def name(self):
        return self.nameLineEdit.text()

    def type(self):
        return self.filterTypeComboBox.currentText()

    def exclusive(self):
        return self.exclusiveCheckBox.isChecked()

    #noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    def accept(self):
        if len(self.nameLineEdit.text()) < 1:
            QMessageBox.critical(self, 'Error saving filter group', 'Please provide a name for the group.')
            return

        QDialog.accept(self)
