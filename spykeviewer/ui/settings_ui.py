# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/rob/Code/Spyke/viewer/spykeviewer/ui/settings.ui'
#
# Created: Tue Aug 14 17:12:13 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName(_fromUtf8("Settings"))
        Settings.resize(647, 438)
        Settings.setStyleSheet(_fromUtf8("QGroupBox {\n"
"     border: 1px solid gray;\n"
"     border-radius: 5px;\n"
"     margin-top: 1ex; /* leave space at the top for the title */\n"
"}\n"
"QGroupBox::title {\n"
"     subcontrol-origin: margin;\n"
"     subcontrol-position: top left; /* position at the top center */\n"
"     padding: 0 2px;\n"
"     left: 10px;\n"
"}"))
        self.gridLayout_2 = QtGui.QGridLayout(Settings)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(Settings)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pathListWidget = QtGui.QListWidget(self.groupBox)
        self.pathListWidget.setObjectName(_fromUtf8("pathListWidget"))
        self.gridLayout.addWidget(self.pathListWidget, 0, 0, 1, 2)
        self.addPathButton = QtGui.QPushButton(self.groupBox)
        self.addPathButton.setObjectName(_fromUtf8("addPathButton"))
        self.gridLayout.addWidget(self.addPathButton, 1, 0, 1, 1)
        self.removePathButton = QtGui.QPushButton(self.groupBox)
        self.removePathButton.setObjectName(_fromUtf8("removePathButton"))
        self.gridLayout.addWidget(self.removePathButton, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 5, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(Settings)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.filterPath = QtGui.QLineEdit(self.groupBox_2)
        self.filterPath.setReadOnly(True)
        self.filterPath.setObjectName(_fromUtf8("filterPath"))
        self.horizontalLayout_2.addWidget(self.filterPath)
        self.changeFilterPathButton = QtGui.QPushButton(self.groupBox_2)
        self.changeFilterPathButton.setObjectName(_fromUtf8("changeFilterPathButton"))
        self.horizontalLayout_2.addWidget(self.changeFilterPathButton)
        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(Settings)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.selectionPath = QtGui.QLineEdit(self.groupBox_3)
        self.selectionPath.setReadOnly(True)
        self.selectionPath.setObjectName(_fromUtf8("selectionPath"))
        self.horizontalLayout.addWidget(self.selectionPath)
        self.changeSelectionPathButton = QtGui.QPushButton(self.groupBox_3)
        self.changeSelectionPathButton.setObjectName(_fromUtf8("changeSelectionPathButton"))
        self.horizontalLayout.addWidget(self.changeSelectionPathButton)
        self.gridLayout_2.addWidget(self.groupBox_3, 0, 0, 1, 1)
        self.groupBox_4 = QtGui.QGroupBox(Settings)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.dataPath = QtGui.QLineEdit(self.groupBox_4)
        self.dataPath.setReadOnly(True)
        self.dataPath.setObjectName(_fromUtf8("dataPath"))
        self.horizontalLayout_3.addWidget(self.dataPath)
        self.changeDataPathButton = QtGui.QPushButton(self.groupBox_4)
        self.changeDataPathButton.setObjectName(_fromUtf8("changeDataPathButton"))
        self.horizontalLayout_3.addWidget(self.changeDataPathButton)
        self.gridLayout_2.addWidget(self.groupBox_4, 2, 0, 1, 1)
        self.groupBox_5 = QtGui.QGroupBox(Settings)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.remoteScriptPath = QtGui.QLineEdit(self.groupBox_5)
        self.remoteScriptPath.setReadOnly(True)
        self.remoteScriptPath.setObjectName(_fromUtf8("remoteScriptPath"))
        self.horizontalLayout_4.addWidget(self.remoteScriptPath)
        self.changeRemoteScriptButton = QtGui.QPushButton(self.groupBox_5)
        self.changeRemoteScriptButton.setObjectName(_fromUtf8("changeRemoteScriptButton"))
        self.horizontalLayout_4.addWidget(self.changeRemoteScriptButton)
        self.gridLayout_2.addWidget(self.groupBox_5, 3, 0, 1, 1)

        self.retranslateUi(Settings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Settings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QtGui.QApplication.translate("Settings", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Settings", "Plugin paths", None, QtGui.QApplication.UnicodeUTF8))
        self.addPathButton.setText(QtGui.QApplication.translate("Settings", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.removePathButton.setText(QtGui.QApplication.translate("Settings", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Settings", "Filter path", None, QtGui.QApplication.UnicodeUTF8))
        self.changeFilterPathButton.setText(QtGui.QApplication.translate("Settings", "Change", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Settings", "Selection path", None, QtGui.QApplication.UnicodeUTF8))
        self.changeSelectionPathButton.setText(QtGui.QApplication.translate("Settings", "Change", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("Settings", "Data path", None, QtGui.QApplication.UnicodeUTF8))
        self.changeDataPathButton.setText(QtGui.QApplication.translate("Settings", "Change", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("Settings", "Remote scipt", None, QtGui.QApplication.UnicodeUTF8))
        self.changeRemoteScriptButton.setText(QtGui.QApplication.translate("Settings", "Change", None, QtGui.QApplication.UnicodeUTF8))

