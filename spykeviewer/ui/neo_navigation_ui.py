# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/rob/Spyke/viewer/spykeviewer/ui/neo_navigation.ui'
#
# Created: Mon Apr 15 15:29:10 2013
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
        self.blocksLabel = QtGui.QLabel(self.dockWidgetContents)
        self.blocksLabel.setObjectName(_fromUtf8("blocksLabel"))
        self.verticalLayout_31.addWidget(self.blocksLabel)
        self.neoBlockList = QtGui.QListView(self.dockWidgetContents)
        self.neoBlockList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.neoBlockList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoBlockList.setObjectName(_fromUtf8("neoBlockList"))
        self.verticalLayout_31.addWidget(self.neoBlockList)
        self.channelGroupsLabel = QtGui.QLabel(self.dockWidgetContents)
        self.channelGroupsLabel.setObjectName(_fromUtf8("channelGroupsLabel"))
        self.verticalLayout_31.addWidget(self.channelGroupsLabel)
        self.neoChannelGroupList = QtGui.QListView(self.dockWidgetContents)
        self.neoChannelGroupList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.neoChannelGroupList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoChannelGroupList.setObjectName(_fromUtf8("neoChannelGroupList"))
        self.verticalLayout_31.addWidget(self.neoChannelGroupList)
        self.channelsLabel = QtGui.QLabel(self.dockWidgetContents)
        self.channelsLabel.setObjectName(_fromUtf8("channelsLabel"))
        self.verticalLayout_31.addWidget(self.channelsLabel)
        self.neoChannelList = QtGui.QListView(self.dockWidgetContents)
        self.neoChannelList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.neoChannelList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoChannelList.setObjectName(_fromUtf8("neoChannelList"))
        self.verticalLayout_31.addWidget(self.neoChannelList)
        self.gridLayout.addLayout(self.verticalLayout_31, 0, 0, 1, 1)
        self.verticalLayout_29 = QtGui.QVBoxLayout()
        self.verticalLayout_29.setObjectName(_fromUtf8("verticalLayout_29"))
        self.segmentsLabel = QtGui.QLabel(self.dockWidgetContents)
        self.segmentsLabel.setObjectName(_fromUtf8("segmentsLabel"))
        self.verticalLayout_29.addWidget(self.segmentsLabel)
        self.neoSegmentList = QtGui.QListView(self.dockWidgetContents)
        self.neoSegmentList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.neoSegmentList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoSegmentList.setObjectName(_fromUtf8("neoSegmentList"))
        self.verticalLayout_29.addWidget(self.neoSegmentList)
        self.unitsLabel = QtGui.QLabel(self.dockWidgetContents)
        self.unitsLabel.setObjectName(_fromUtf8("unitsLabel"))
        self.verticalLayout_29.addWidget(self.unitsLabel)
        self.neoUnitList = QtGui.QListView(self.dockWidgetContents)
        self.neoUnitList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.neoUnitList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.neoUnitList.setObjectName(_fromUtf8("neoUnitList"))
        self.verticalLayout_29.addWidget(self.neoUnitList)
        self.gridLayout.addLayout(self.verticalLayout_29, 0, 1, 1, 1)
        neoNavigationDock.setWidget(self.dockWidgetContents)

        self.retranslateUi(neoNavigationDock)
        QtCore.QMetaObject.connectSlotsByName(neoNavigationDock)

    def retranslateUi(self, neoNavigationDock):
        neoNavigationDock.setWindowTitle(QtGui.QApplication.translate("neoNavigationDock", "Navigation", None, QtGui.QApplication.UnicodeUTF8))
        self.blocksLabel.setText(QtGui.QApplication.translate("neoNavigationDock", "Blocks:", None, QtGui.QApplication.UnicodeUTF8))
        self.channelGroupsLabel.setText(QtGui.QApplication.translate("neoNavigationDock", "Channel Groups:", None, QtGui.QApplication.UnicodeUTF8))
        self.channelsLabel.setText(QtGui.QApplication.translate("neoNavigationDock", "Channels:", None, QtGui.QApplication.UnicodeUTF8))
        self.segmentsLabel.setText(QtGui.QApplication.translate("neoNavigationDock", "Segments:", None, QtGui.QApplication.UnicodeUTF8))
        self.unitsLabel.setText(QtGui.QApplication.translate("neoNavigationDock", "Units:", None, QtGui.QApplication.UnicodeUTF8))

