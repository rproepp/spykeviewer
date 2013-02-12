# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/rob/Spyke/viewer/spykeviewer/ui/neo_navigation.ui'
#
# Created: Tue Feb 12 11:59:52 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_neoNavigationDock(object):
    def setupUi(self, neoNavigationDock):
        neoNavigationDock.setObjectName(_fromUtf8("neoNavigationDock"))
        neoNavigationDock.resize(352, 559)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_31 = QtGui.QVBoxLayout()
        self.verticalLayout_31.setObjectName(_fromUtf8("verticalLayout_31"))
        self.label_34 = QtGui.QLabel(self.dockWidgetContents)
        self.label_34.setObjectName(_fromUtf8("label_34"))
        self.verticalLayout_31.addWidget(self.label_34)
        self.neoBlockList = QtGui.QListWidget(self.dockWidgetContents)
        self.neoBlockList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoBlockList.setObjectName(_fromUtf8("neoBlockList"))
        self.verticalLayout_31.addWidget(self.neoBlockList)
        self.label_36 = QtGui.QLabel(self.dockWidgetContents)
        self.label_36.setObjectName(_fromUtf8("label_36"))
        self.verticalLayout_31.addWidget(self.label_36)
        self.neoChannelGroupList = QtGui.QListWidget(self.dockWidgetContents)
        self.neoChannelGroupList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoChannelGroupList.setObjectName(_fromUtf8("neoChannelGroupList"))
        self.verticalLayout_31.addWidget(self.neoChannelGroupList)
        self.label_37 = QtGui.QLabel(self.dockWidgetContents)
        self.label_37.setObjectName(_fromUtf8("label_37"))
        self.verticalLayout_31.addWidget(self.label_37)
        self.neoChannelList = QtGui.QListWidget(self.dockWidgetContents)
        self.neoChannelList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoChannelList.setObjectName(_fromUtf8("neoChannelList"))
        self.verticalLayout_31.addWidget(self.neoChannelList)
        self.gridLayout.addLayout(self.verticalLayout_31, 0, 0, 1, 1)
        self.verticalLayout_29 = QtGui.QVBoxLayout()
        self.verticalLayout_29.setObjectName(_fromUtf8("verticalLayout_29"))
        self.label_35 = QtGui.QLabel(self.dockWidgetContents)
        self.label_35.setObjectName(_fromUtf8("label_35"))
        self.verticalLayout_29.addWidget(self.label_35)
        self.neoSegmentList = QtGui.QListWidget(self.dockWidgetContents)
        self.neoSegmentList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoSegmentList.setObjectName(_fromUtf8("neoSegmentList"))
        self.verticalLayout_29.addWidget(self.neoSegmentList)
        self.label_38 = QtGui.QLabel(self.dockWidgetContents)
        self.label_38.setObjectName(_fromUtf8("label_38"))
        self.verticalLayout_29.addWidget(self.label_38)
        self.neoUnitList = QtGui.QListWidget(self.dockWidgetContents)
        self.neoUnitList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoUnitList.setObjectName(_fromUtf8("neoUnitList"))
        self.verticalLayout_29.addWidget(self.neoUnitList)
        self.gridLayout.addLayout(self.verticalLayout_29, 0, 1, 1, 1)
        neoNavigationDock.setWidget(self.dockWidgetContents)

        self.retranslateUi(neoNavigationDock)
        QtCore.QMetaObject.connectSlotsByName(neoNavigationDock)

    def retranslateUi(self, neoNavigationDock):
        neoNavigationDock.setWindowTitle(QtGui.QApplication.translate("neoNavigationDock", "Navigation", None, QtGui.QApplication.UnicodeUTF8))
        self.label_34.setText(QtGui.QApplication.translate("neoNavigationDock", "Blocks:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_36.setText(QtGui.QApplication.translate("neoNavigationDock", "Channel Groups:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_37.setText(QtGui.QApplication.translate("neoNavigationDock", "Channels:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_35.setText(QtGui.QApplication.translate("neoNavigationDock", "Segments:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_38.setText(QtGui.QApplication.translate("neoNavigationDock", "Units:", None, QtGui.QApplication.UnicodeUTF8))

