from PyQt4.QtCore import QEvent
from PyQt4.QtGui import (QFileDialog, QListView,
                         QPushButton, QDialog, QTreeView)


class DirFilesDialog(QFileDialog):
    """ A file dialog that allows to choose multiple files and folders.
    """
    def __init__(self, parent=None, caption='', directory='', filter=''):
        super(DirFilesDialog, self).__init__(parent, caption,
                                             directory, filter)

        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setAcceptMode(QFileDialog.AcceptOpen)
        self.setFileMode(QFileDialog.Directory)
        self.setNameFilter('All files or folders (*)')
        self.setNameFilterDetailsVisible(False)

        self.list_view = self.findChild(QListView, 'listView')
        if self.list_view:
            self.list_view.setSelectionMode(QListView.ExtendedSelection)
            sel_model = self.list_view.selectionModel()
            sel_model.selectionChanged.connect(self.enable_update)

        self.tree_view = self.findChild(QTreeView, 'listView')
        if self.tree_view:
            self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)
            sel_model = self.tree_view.selectionModel()
            sel_model.selectionChanged.connect(self.enable_update)

        for b in self.findChildren(QPushButton):
            if 'choose' in b.text().lower():
                self.button = b
                b.installEventFilter(self)
                b.clicked.disconnect()
                b.clicked.connect(self.choose_clicked)
                b.setEnabled(False)
                break

    def eventFilter(self, watched, event):
        if event.type() == QEvent.EnabledChange:
            if not watched.isEnabled():
                if self.list_view:
                    if self.list_view.selectionModel().selectedIndexes():
                        watched.setEnabled(True)
                elif self.tree_view:
                    if self.tree_view.selectionModel().selectedIndexes():
                        watched.setEnabled(True)

        return super(QFileDialog, self).eventFilter(watched, event)

    def enable_update(self):
        if self.list_view:
            if self.list_view.selectionModel().selectedIndexes():
                self.button.setEnabled(True)
            else:
                self.button.setEnabled(False)
        elif self.tree_view:
            if self.tree_view.selectionModel().selectedIndexes():
                self.button.setEnabled(True)
            else:
                self.button.setEnabled(False)

    def choose_clicked(self):
        self.done(QDialog.Accepted)