# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/rob/Spyke/viewer/spykeviewer/ui/main.ui'
#
# Created: Mon Jun 10 15:14:02 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(819, 867)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(790, 580))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/Application/Main")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet(_fromUtf8("QGroupBox {\n"
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
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        MainWindow.setDockOptions(QtGui.QMainWindow.AllowNestedDocks|QtGui.QMainWindow.AllowTabbedDocks|QtGui.QMainWindow.AnimatedDocks)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralWidget)
        self.horizontalLayout_2.setMargin(4)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        MainWindow.setCentralWidget(self.centralWidget)
        self.mainMenu = QtGui.QMenuBar(MainWindow)
        self.mainMenu.setGeometry(QtCore.QRect(0, 0, 819, 25))
        self.mainMenu.setObjectName(_fromUtf8("mainMenu"))
        self.menuFile = QtGui.QMenu(self.mainMenu)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuRead_Mode = QtGui.QMenu(self.menuFile)
        self.menuRead_Mode.setObjectName(_fromUtf8("menuRead_Mode"))
        self.menuHelp = QtGui.QMenu(self.mainMenu)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuSelections = QtGui.QMenu(self.mainMenu)
        self.menuSelections.setObjectName(_fromUtf8("menuSelections"))
        self.menuPlugins = QtGui.QMenu(self.mainMenu)
        self.menuPlugins.setObjectName(_fromUtf8("menuPlugins"))
        self.menuFilter = QtGui.QMenu(self.mainMenu)
        self.menuFilter.setObjectName(_fromUtf8("menuFilter"))
        MainWindow.setMenuBar(self.mainMenu)
        self.consoleDock = QtGui.QDockWidget(MainWindow)
        self.consoleDock.setObjectName(_fromUtf8("consoleDock"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout_19 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_19.setObjectName(_fromUtf8("verticalLayout_19"))
        self.consoleDock.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.consoleDock)
        self.variableExplorerDock = QtGui.QDockWidget(MainWindow)
        self.variableExplorerDock.setObjectName(_fromUtf8("variableExplorerDock"))
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName(_fromUtf8("dockWidgetContents_2"))
        self.variableExplorerDock.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.variableExplorerDock)
        self.historyDock = QtGui.QDockWidget(MainWindow)
        self.historyDock.setObjectName(_fromUtf8("historyDock"))
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName(_fromUtf8("dockWidgetContents_3"))
        self.historyDock.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.historyDock)
        self.pluginDock = QtGui.QDockWidget(MainWindow)
        self.pluginDock.setObjectName(_fromUtf8("pluginDock"))
        self.dockWidgetContents_6 = QtGui.QWidget()
        self.dockWidgetContents_6.setObjectName(_fromUtf8("dockWidgetContents_6"))
        self.gridLayout_11 = QtGui.QGridLayout(self.dockWidgetContents_6)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.pluginsTreeView = QtGui.QTreeView(self.dockWidgetContents_6)
        self.pluginsTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.pluginsTreeView.setUniformRowHeights(True)
        self.pluginsTreeView.setHeaderHidden(True)
        self.pluginsTreeView.setObjectName(_fromUtf8("pluginsTreeView"))
        self.pluginsTreeView.header().setVisible(False)
        self.pluginsTreeView.header().setDefaultSectionSize(0)
        self.gridLayout_11.addWidget(self.pluginsTreeView, 0, 0, 1, 2)
        self.pluginDock.setWidget(self.dockWidgetContents_6)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.pluginDock)
        self.filesDock = QtGui.QDockWidget(MainWindow)
        self.filesDock.setObjectName(_fromUtf8("filesDock"))
        self.dockWidgetContents_8 = QtGui.QWidget()
        self.dockWidgetContents_8.setObjectName(_fromUtf8("dockWidgetContents_8"))
        self.gridLayout_6 = QtGui.QGridLayout(self.dockWidgetContents_8)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.fileTreeView = QtGui.QTreeView(self.dockWidgetContents_8)
        self.fileTreeView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.fileTreeView.setUniformRowHeights(True)
        self.fileTreeView.setHeaderHidden(True)
        self.fileTreeView.setObjectName(_fromUtf8("fileTreeView"))
        self.fileTreeView.header().setVisible(False)
        self.fileTreeView.header().setCascadingSectionResizes(False)
        self.fileTreeView.header().setStretchLastSection(False)
        self.gridLayout_6.addWidget(self.fileTreeView, 0, 0, 1, 1)
        self.loadFilesButton = QtGui.QPushButton(self.dockWidgetContents_8)
        self.loadFilesButton.setObjectName(_fromUtf8("loadFilesButton"))
        self.gridLayout_6.addWidget(self.loadFilesButton, 1, 0, 1, 1)
        self.filesDock.setWidget(self.dockWidgetContents_8)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.filesDock)
        self.filterToolbar = QtGui.QToolBar(MainWindow)
        self.filterToolbar.setObjectName(_fromUtf8("filterToolbar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.filterToolbar)
        self.pluginToolBar = QtGui.QToolBar(MainWindow)
        self.pluginToolBar.setObjectName(_fromUtf8("pluginToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.pluginToolBar)
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setMenuRole(QtGui.QAction.QuitRole)
        self.actionExit.setIconVisibleInMenu(False)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionSave_selection = QtGui.QAction(MainWindow)
        self.actionSave_selection.setObjectName(_fromUtf8("actionSave_selection"))
        self.actionLoad_selection = QtGui.QAction(MainWindow)
        self.actionLoad_selection.setObjectName(_fromUtf8("actionLoad_selection"))
        self.actionAbout = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/Application/Info")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon1)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionSwitch_Modes = QtGui.QAction(MainWindow)
        self.actionSwitch_Modes.setVisible(False)
        self.actionSwitch_Modes.setObjectName(_fromUtf8("actionSwitch_Modes"))
        self.actionNewSelection = QtGui.QAction(MainWindow)
        self.actionNewSelection.setObjectName(_fromUtf8("actionNewSelection"))
        self.actionClearCache = QtGui.QAction(MainWindow)
        self.actionClearCache.setVisible(True)
        self.actionClearCache.setObjectName(_fromUtf8("actionClearCache"))
        self.actionSave_Selected_Data = QtGui.QAction(MainWindow)
        self.actionSave_Selected_Data.setObjectName(_fromUtf8("actionSave_Selected_Data"))
        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName(_fromUtf8("actionSettings"))
        self.actionClearSelections = QtGui.QAction(MainWindow)
        self.actionClearSelections.setObjectName(_fromUtf8("actionClearSelections"))
        self.actionNewPlugin = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/New")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewPlugin.setIcon(icon2)
        self.actionNewPlugin.setObjectName(_fromUtf8("actionNewPlugin"))
        self.actionEditPlugin = QtGui.QAction(MainWindow)
        self.actionEditPlugin.setEnabled(False)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Edit")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEditPlugin.setIcon(icon3)
        self.actionEditPlugin.setObjectName(_fromUtf8("actionEditPlugin"))
        self.actionRefreshPlugins = QtGui.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Reload")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefreshPlugins.setIcon(icon4)
        self.actionRefreshPlugins.setObjectName(_fromUtf8("actionRefreshPlugins"))
        self.actionSavePlugin = QtGui.QAction(MainWindow)
        self.actionSavePlugin.setEnabled(False)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Save")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSavePlugin.setIcon(icon5)
        self.actionSavePlugin.setObjectName(_fromUtf8("actionSavePlugin"))
        self.actionConfigurePlugin = QtGui.QAction(MainWindow)
        self.actionConfigurePlugin.setEnabled(False)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Config")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionConfigurePlugin.setIcon(icon6)
        self.actionConfigurePlugin.setObjectName(_fromUtf8("actionConfigurePlugin"))
        self.actionRunPlugin = QtGui.QAction(MainWindow)
        self.actionRunPlugin.setEnabled(False)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Run")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRunPlugin.setIcon(icon7)
        self.actionRunPlugin.setObjectName(_fromUtf8("actionRunPlugin"))
        self.actionRemotePlugin = QtGui.QAction(MainWindow)
        self.actionRemotePlugin.setEnabled(False)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Remote")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRemotePlugin.setIcon(icon8)
        self.actionRemotePlugin.setObjectName(_fromUtf8("actionRemotePlugin"))
        self.actionNewFilter = QtGui.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/Filter/New Filter")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewFilter.setIcon(icon9)
        self.actionNewFilter.setObjectName(_fromUtf8("actionNewFilter"))
        self.actionCopyFilter = QtGui.QAction(MainWindow)
        self.actionCopyFilter.setEnabled(False)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(_fromUtf8(":/Filter/Copy Filter")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCopyFilter.setIcon(icon10)
        self.actionCopyFilter.setObjectName(_fromUtf8("actionCopyFilter"))
        self.actionEditFilter = QtGui.QAction(MainWindow)
        self.actionEditFilter.setEnabled(False)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(_fromUtf8(":/Filter/Edit Filter")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEditFilter.setIcon(icon11)
        self.actionEditFilter.setObjectName(_fromUtf8("actionEditFilter"))
        self.actionDeleteFilter = QtGui.QAction(MainWindow)
        self.actionDeleteFilter.setEnabled(False)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(_fromUtf8(":/Filter/Remove Filter")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDeleteFilter.setIcon(icon12)
        self.actionDeleteFilter.setObjectName(_fromUtf8("actionDeleteFilter"))
        self.actionNewFilterGroup = QtGui.QAction(MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(_fromUtf8(":/Filter/New Filter Group")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewFilterGroup.setIcon(icon13)
        self.actionNewFilterGroup.setObjectName(_fromUtf8("actionNewFilterGroup"))
        self.actionSavePluginAs = QtGui.QAction(MainWindow)
        self.actionSavePluginAs.setEnabled(False)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Save As")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSavePluginAs.setIcon(icon14)
        self.actionSavePluginAs.setObjectName(_fromUtf8("actionSavePluginAs"))
        self.actionDocumentation = QtGui.QAction(MainWindow)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(_fromUtf8(":/Application/Help")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDocumentation.setIcon(icon15)
        self.actionDocumentation.setObjectName(_fromUtf8("actionDocumentation"))
        self.actionSave_Data = QtGui.QAction(MainWindow)
        self.actionSave_Data.setObjectName(_fromUtf8("actionSave_Data"))
        self.actionShowPluginFolder = QtGui.QAction(MainWindow)
        self.actionShowPluginFolder.setEnabled(False)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Show Folder")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowPluginFolder.setIcon(icon16)
        self.actionShowPluginFolder.setObjectName(_fromUtf8("actionShowPluginFolder"))
        self.actionEdit_Startup_Script = QtGui.QAction(MainWindow)
        self.actionEdit_Startup_Script.setObjectName(_fromUtf8("actionEdit_Startup_Script"))
        self.actionRestorePluginConfigurations = QtGui.QAction(MainWindow)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(_fromUtf8(":/Plugins/Restore Config")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRestorePluginConfigurations.setIcon(icon17)
        self.actionRestorePluginConfigurations.setObjectName(_fromUtf8("actionRestorePluginConfigurations"))
        self.actionLoad_Python_File = QtGui.QAction(MainWindow)
        self.actionLoad_Python_File.setObjectName(_fromUtf8("actionLoad_Python_File"))
        self.actionFull_Load = QtGui.QAction(MainWindow)
        self.actionFull_Load.setCheckable(True)
        self.actionFull_Load.setChecked(True)
        self.actionFull_Load.setObjectName(_fromUtf8("actionFull_Load"))
        self.actionLazy_Load = QtGui.QAction(MainWindow)
        self.actionLazy_Load.setCheckable(True)
        self.actionLazy_Load.setObjectName(_fromUtf8("actionLazy_Load"))
        self.actionLoad_Data = QtGui.QAction(MainWindow)
        self.actionLoad_Data.setObjectName(_fromUtf8("actionLoad_Data"))
        self.menuRead_Mode.addAction(self.actionFull_Load)
        self.menuRead_Mode.addAction(self.actionLazy_Load)
        self.menuFile.addAction(self.actionLoad_Data)
        self.menuFile.addAction(self.menuRead_Mode.menuAction())
        self.menuFile.addAction(self.actionClearCache)
        self.menuFile.addAction(self.actionSave_Data)
        self.menuFile.addAction(self.actionSave_Selected_Data)
        self.menuFile.addAction(self.actionSwitch_Modes)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_selection)
        self.menuFile.addAction(self.actionLoad_selection)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoad_Python_File)
        self.menuFile.addAction(self.actionEdit_Startup_Script)
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionDocumentation)
        self.menuHelp.addAction(self.actionAbout)
        self.menuSelections.addAction(self.actionNewSelection)
        self.menuSelections.addAction(self.actionClearSelections)
        self.menuSelections.addSeparator()
        self.menuPlugins.addAction(self.actionRunPlugin)
        self.menuPlugins.addAction(self.actionRemotePlugin)
        self.menuPlugins.addAction(self.actionConfigurePlugin)
        self.menuPlugins.addSeparator()
        self.menuPlugins.addAction(self.actionRefreshPlugins)
        self.menuPlugins.addAction(self.actionRestorePluginConfigurations)
        self.menuPlugins.addSeparator()
        self.menuPlugins.addAction(self.actionNewPlugin)
        self.menuPlugins.addAction(self.actionEditPlugin)
        self.menuPlugins.addAction(self.actionSavePlugin)
        self.menuPlugins.addAction(self.actionSavePluginAs)
        self.menuPlugins.addAction(self.actionShowPluginFolder)
        self.menuFilter.addAction(self.actionNewFilter)
        self.menuFilter.addAction(self.actionNewFilterGroup)
        self.menuFilter.addAction(self.actionCopyFilter)
        self.menuFilter.addAction(self.actionEditFilter)
        self.menuFilter.addAction(self.actionDeleteFilter)
        self.mainMenu.addAction(self.menuFile.menuAction())
        self.mainMenu.addAction(self.menuSelections.menuAction())
        self.mainMenu.addAction(self.menuFilter.menuAction())
        self.mainMenu.addAction(self.menuPlugins.menuAction())
        self.mainMenu.addAction(self.menuHelp.menuAction())
        self.filterToolbar.addAction(self.actionNewFilter)
        self.filterToolbar.addAction(self.actionNewFilterGroup)
        self.filterToolbar.addAction(self.actionCopyFilter)
        self.filterToolbar.addAction(self.actionEditFilter)
        self.filterToolbar.addAction(self.actionDeleteFilter)
        self.pluginToolBar.addAction(self.actionNewPlugin)
        self.pluginToolBar.addAction(self.actionEditPlugin)
        self.pluginToolBar.addAction(self.actionSavePlugin)
        self.pluginToolBar.addAction(self.actionSavePluginAs)
        self.pluginToolBar.addAction(self.actionRefreshPlugins)
        self.pluginToolBar.addAction(self.actionConfigurePlugin)
        self.pluginToolBar.addAction(self.actionRunPlugin)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Spyke Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuRead_Mode.setTitle(QtGui.QApplication.translate("MainWindow", "Read Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSelections.setTitle(QtGui.QApplication.translate("MainWindow", "&Selections", None, QtGui.QApplication.UnicodeUTF8))
        self.menuPlugins.setTitle(QtGui.QApplication.translate("MainWindow", "&Plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFilter.setTitle(QtGui.QApplication.translate("MainWindow", "&Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.consoleDock.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Console", None, QtGui.QApplication.UnicodeUTF8))
        self.variableExplorerDock.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Variable Explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.historyDock.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Command History", None, QtGui.QApplication.UnicodeUTF8))
        self.pluginDock.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.filesDock.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Files", None, QtGui.QApplication.UnicodeUTF8))
        self.loadFilesButton.setText(QtGui.QApplication.translate("MainWindow", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.filterToolbar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Filter Toolbar", None, QtGui.QApplication.UnicodeUTF8))
        self.pluginToolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Plugin Toolbar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("MainWindow", "&Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_selection.setText(QtGui.QApplication.translate("MainWindow", "&Save Selection Set...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad_selection.setText(QtGui.QApplication.translate("MainWindow", "&Load Selection Set...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "&About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSwitch_Modes.setText(QtGui.QApplication.translate("MainWindow", "Switch Modes", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewSelection.setText(QtGui.QApplication.translate("MainWindow", "&New", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClearCache.setText(QtGui.QApplication.translate("MainWindow", "&Clear Data", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Selected_Data.setText(QtGui.QApplication.translate("MainWindow", "Save Selected Data &as...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setText(QtGui.QApplication.translate("MainWindow", "Settings...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClearSelections.setText(QtGui.QApplication.translate("MainWindow", "&Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewPlugin.setText(QtGui.QApplication.translate("MainWindow", "&New Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewPlugin.setToolTip(QtGui.QApplication.translate("MainWindow", "Create a new plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEditPlugin.setText(QtGui.QApplication.translate("MainWindow", "&Edit Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEditPlugin.setToolTip(QtGui.QApplication.translate("MainWindow", "Edit selected plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEditPlugin.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+E", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRefreshPlugins.setText(QtGui.QApplication.translate("MainWindow", "&Refresh Plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRefreshPlugins.setToolTip(QtGui.QApplication.translate("MainWindow", "Refresh all plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRefreshPlugins.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSavePlugin.setText(QtGui.QApplication.translate("MainWindow", "&Save Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSavePlugin.setToolTip(QtGui.QApplication.translate("MainWindow", "Save current file", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSavePlugin.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConfigurePlugin.setText(QtGui.QApplication.translate("MainWindow", "&Configure Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConfigurePlugin.setToolTip(QtGui.QApplication.translate("MainWindow", "Configure selected plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConfigurePlugin.setShortcut(QtGui.QApplication.translate("MainWindow", "F6", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRunPlugin.setText(QtGui.QApplication.translate("MainWindow", "Run &Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRunPlugin.setToolTip(QtGui.QApplication.translate("MainWindow", "Run selected plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRunPlugin.setShortcut(QtGui.QApplication.translate("MainWindow", "F5", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRemotePlugin.setText(QtGui.QApplication.translate("MainWindow", "Start with Remote Script", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRemotePlugin.setToolTip(QtGui.QApplication.translate("MainWindow", "Start selected plugin with Remote Script", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRemotePlugin.setShortcut(QtGui.QApplication.translate("MainWindow", "F9", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewFilter.setText(QtGui.QApplication.translate("MainWindow", "&New Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewFilter.setToolTip(QtGui.QApplication.translate("MainWindow", "Create a new filter", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopyFilter.setText(QtGui.QApplication.translate("MainWindow", "&Copy", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopyFilter.setToolTip(QtGui.QApplication.translate("MainWindow", "Duplicate selected filter or group", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEditFilter.setText(QtGui.QApplication.translate("MainWindow", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEditFilter.setToolTip(QtGui.QApplication.translate("MainWindow", "Edit selected filter or filter group", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDeleteFilter.setText(QtGui.QApplication.translate("MainWindow", "&Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDeleteFilter.setToolTip(QtGui.QApplication.translate("MainWindow", "Delete selected filter or filter group", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewFilterGroup.setText(QtGui.QApplication.translate("MainWindow", "New Filter &Group", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewFilterGroup.setToolTip(QtGui.QApplication.translate("MainWindow", "Create a new filter group", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSavePluginAs.setText(QtGui.QApplication.translate("MainWindow", "Save Plugin &as...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSavePluginAs.setToolTip(QtGui.QApplication.translate("MainWindow", "Save current file as...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDocumentation.setText(QtGui.QApplication.translate("MainWindow", "&Documentation", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDocumentation.setToolTip(QtGui.QApplication.translate("MainWindow", "Open documentation website\n"
"(requires Internet access)", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Data.setText(QtGui.QApplication.translate("MainWindow", "Save &Data as...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShowPluginFolder.setText(QtGui.QApplication.translate("MainWindow", "&Open containing folder...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShowPluginFolder.setToolTip(QtGui.QApplication.translate("MainWindow", "Open folder that contains selected plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEdit_Startup_Script.setText(QtGui.QApplication.translate("MainWindow", "Edit Startup Script", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRestorePluginConfigurations.setText(QtGui.QApplication.translate("MainWindow", "Restore Plugin configurations", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRestorePluginConfigurations.setToolTip(QtGui.QApplication.translate("MainWindow", "Restore Plugin configurations to their default values", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad_Python_File.setText(QtGui.QApplication.translate("MainWindow", "Load &Python File...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFull_Load.setText(QtGui.QApplication.translate("MainWindow", "Full Load", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLazy_Load.setText(QtGui.QApplication.translate("MainWindow", "Lazy Load", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad_Data.setText(QtGui.QApplication.translate("MainWindow", "Load Data...", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc
