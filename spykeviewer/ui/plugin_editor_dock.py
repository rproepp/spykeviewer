import os.path
from PyQt4.QtGui import (QDockWidget, QWidget, QFileDialog, QPushButton,
                         QGridLayout, QMessageBox, QFont, QTabWidget)
from PyQt4.QtCore import Qt, pyqtSignal

from spyderlib.widgets.sourcecode.codeeditor import CodeEditor


class PluginEditorDock(QDockWidget):
    """ A dock for editing plugins.
    """

    template_code = \
"""from spykeutils.plugin import analysis_plugin, gui_data

class SamplePlugin(analysis_plugin.AnalysisPlugin):
    def get_name(self):
        return 'New plugin'

    def start(self, current, selections):
        print 'Plugin started.'
"""

    plugin_saved = pyqtSignal(str)

    def __init__(self, title='Plugin Editor', parent=None):
        QDockWidget.__init__(self, title, parent)
        self.setupUi()

    def populate_groups(self):
        self.filterGroupComboBox.clear()
        self.filterGroupComboBox.addItem('')
        for g in sorted(self.groups[self.filterTypeComboBox.currentText()]):
            self.filterGroupComboBox.addItem(g)

    def setupUi(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_file)

        self.content_widget = QWidget()
        layout = QGridLayout(self.content_widget)
        layout.addWidget(self.tabs)

        self.setWidget(self.content_widget)

    def _setup_editor(self):
        font = QFont('Some font that does not exist')
        font.setStyleHint(font.TypeWriter, font.PreferDefault)
        editor = CodeEditor()
        editor.setup_editor(linenumbers=True, language='py',
            scrollflagarea=False, codecompletion_enter=True,
            tab_mode=False, edge_line=False, font=font,
            codecompletion_auto=True, go_to_definition=True,
            codecompletion_single=True)
        editor.setCursor(Qt.IBeamCursor)
        editor.horizontalScrollBar().setCursor(Qt.ArrowCursor)
        editor.verticalScrollBar().setCursor(Qt.ArrowCursor)
        return editor

    def _finanlize_new_editor(self, editor, tab_name):
        editor.file_was_changed = False
        editor.textChanged.connect(lambda: self.file_changed(editor))

        self.tabs.addTab(editor, tab_name)
        self.tabs.setCurrentWidget(editor)

        self.setVisible(True)
        self.raise_()

    def new_file(self, path):
        editor = self._setup_editor()
        editor.file_name = path
        editor.set_text(self.template_code)
        self._finanlize_new_editor(editor, 'New Plugin')

    def add_file(self, file_name):
        if file_name and not file_name.endswith('py'):
            QMessageBox.warning(self, 'Cannot load file',
                'Only Python files are supported for editing')
            return

        editor = self._setup_editor()
        editor.file_name = file_name
        editor.set_text_from_file(file_name)
        tab_name = os.path.split(file_name)[1]
        self._finanlize_new_editor(editor, tab_name)

    def close_file(self, tab_index):
        if self.tabs.widget(tab_index).file_was_changed:
            fname = os.path.split(self.tabs.widget(tab_index).file_name)[1]
            if not fname:
                fname = 'New Plugin'
            ans = QMessageBox.question(self, 'File was changed',
                'Do you want to save "%s" before closing?' % fname,
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if ans == QMessageBox.Yes:
                return self.save_file(self.tabs.widget(tab_index), False)
            elif ans == QMessageBox.Cancel:
                return False
        self.tabs.removeTab(tab_index)
        return True

    def closeEvent(self, event):
        if not self.close_all():
            event.ignore()
        else:
            event.accept()

    def close_all(self):
        while self.tabs.count():
            if not self.close_file(0):
                return False
        return True

    def file_changed(self, editor):
        editor.file_was_changed = True

        fname = os.path.split(editor.file_name)[1]
        if not fname:
            fname = 'New Plugin'
        text = '*' + fname

        self.tabs.setTabText(self.tabs.indexOf(editor), text)

    def code(self):
        return [self.tabs.currentWidget().get_text_line(l)
                for l in xrange(self.tabs.currentWidget().get_line_count())]


    def code_has_errors(self):
        code = '\n'.join(self.code())
        try:
            compile(code, '<filter>', 'exec')
        except SyntaxError as e:
            return e.msg + ' (Line %d)' % (e.lineno)
        return None

    def save_file(self, editor, force_dialog):
        if not editor:
            return
        if force_dialog or not editor.file_name.endswith('py'):
            d = QFileDialog(self, 'Choose where to save plugin',
                self.tabs.currentWidget().file_name)
            d.setAcceptMode(QFileDialog.AcceptSave)
            d.setNameFilter("Python files (*.py)")
            d.setDefaultSuffix('py')
            if d.exec_():
                editor.file_name = str(d.selectedFiles()[0])
            else:
                return False

        err = self.code_has_errors()
        if err:
            QMessageBox.critical(self, 'Error saving plugin',
                'Compile error:\n' + err)
            return False

        f = open(editor.file_name, 'w')
        f.write('\n'.join(self.code()))
        f.close()

        editor.file_was_changed = False
        fname = os.path.split(editor.file_name)[1]
        self.tabs.setTabText(self.tabs.indexOf(editor), fname)
        self.plugin_saved.emit(editor.file_name)
        return True

    def save_current(self, force_dialog=False):
        editor = self.tabs.currentWidget()
        self.save_file(editor, force_dialog)
