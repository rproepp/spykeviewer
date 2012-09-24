import os

from PyQt4.QtGui import QDialog, QFileDialog
from PyQt4.QtCore import Qt

from settings_ui import Ui_Settings

class SettingsWindow(QDialog, Ui_Settings):
    def __init__(self, selection_path, filter_path, data_path,
                 remote_script, plugin_paths, parent = None):
        QDialog.__init__(self, parent)

        self.setupUi(self)
        self.selectionPath.setText(selection_path)
        self.filterPath.setText(filter_path)
        self.dataPath.setText(data_path)
        self.remoteScriptPath.setText(remote_script)
        for p in plugin_paths:
            self.pathListWidget.addItem(p)

    def selection_path(self):
        return self.selectionPath.text()

    def filter_path(self):
        return self.filterPath.text()

    def data_path(self):
        return self.dataPath.text()

    def remote_script(self):
        return self.remoteScriptPath.text()

    def plugin_paths(self):
        return [i.text() for i in self.pathListWidget.findItems('*',
            Qt.MatchWrap | Qt.MatchWildcard)]

    def _makeDirDialog(self, name):
        d = QFileDialog(self, name, os.getcwd())
        d.setAcceptMode(QFileDialog.AcceptOpen)
        d.setFileMode(QFileDialog.Directory)
        d.setOption(QFileDialog.ShowDirsOnly, True)
        d.setNameFilter("Directories")
        return d

    def on_changeSelectionPathButton_pressed(self):
        d = self._makeDirDialog('Choose selection path')
        if d.exec_() == d.Accepted:
            filename = str(d.selectedFiles()[0])
            self.selectionPath.setText(filename)
        else:
            return

    def on_changeFilterPathButton_pressed(self):
        d = self._makeDirDialog('Choose filter path')
        if d.exec_() == d.Accepted:
            filename = str(d.selectedFiles()[0])
            self.filterPath.setText(filename)
        else:
            return

    def on_changeDataPathButton_pressed(self):
        d = self._makeDirDialog('Choose data path')
        if d.exec_() == d.Accepted:
            filename = str(d.selectedFiles()[0])
            self.dataPath.setText(filename)
        else:
            return

    def on_changeRemoteScriptButton_pressed(self):
        d = QFileDialog(self, 'Choose remote script', self.remote_script())
        d.setAcceptMode(QFileDialog.AcceptOpen)
        d.setFileMode(QFileDialog.ExistingFile)
        if d.exec_() == d.Accepted:
            filename = str(d.selectedFiles()[0])
            self.remoteScriptPath.setText(filename)
        else:
            return

    def on_addPathButton_pressed(self):
        d = self._makeDirDialog('Choose plugin path')
        if d.exec_() == d.Accepted:
            filename = str(d.selectedFiles()[0])
            if filename not in self.plugin_paths():
                self.pathListWidget.addItem(filename)
        else:
            return

    def on_removePathButton_pressed(self):
        if not self.pathListWidget.currentItem():
            return
        self.pathListWidget.takeItem(self.pathListWidget.currentRow())