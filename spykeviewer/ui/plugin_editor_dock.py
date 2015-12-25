import os
import re
from PyQt4.QtGui import (QDockWidget, QWidget, QFileDialog, QGridLayout,
                         QMessageBox, QFont, QTabWidget, QTextCursor,
                         QDesktopServices)
from PyQt4.QtCore import Qt, pyqtSignal, SIGNAL

from spyderlib.widgets.sourcecode import codeeditor
from spyderlib.widgets.editor import ThreadManager
try:  # Spyder < 2.2.0
    from spyderlib.utils.module_completion import moduleCompletion \
        as module_completion
except ImportError:  # Spyder >= 2.2.0beta3
    try:
        from spyderlib.utils.module_completion import module_completion
    except ImportError:  # Spyder >= 2.3.0
        try:
            from spyderlib.utils.introspection.module_completion import \
                module_completion
        except ImportError:  # Spyder >= 2.3.2
            from spyderlib.utils.introspection import module_completion

try:
    from spyderlib.utils.dochelpers import getsignaturesfromtext
except ImportError:  # Spyder >= 2.3.0
    from spyderlib.utils.dochelpers import getsignaturefromtext as \
        getsignaturesfromtext
from spyderlib.widgets.findreplace import FindReplace


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
    file_available = pyqtSignal(bool)

    def __init__(self, title='Plugin Editor', default_path=None, parent=None):
        QDockWidget.__init__(self, title, parent)
        self.setupUi()

        self.thread_manager = ThreadManager(self)
        try:
            self.rope_project = codeeditor.get_rope_project()
        except (IOError, AttributeError):  # Might happen when frozen
            self.rope_project = None

        data_path = QDesktopServices.storageLocation(
            QDesktopServices.DataLocation)
        self.default_path = default_path or os.getcwd()
        self.rope_temp_path = os.path.join(data_path, '.temp')
        self.tabs.currentChanged.connect(self._tab_changed)
        self.enter_completion = True

    def _tab_changed(self, tab):
        self.file_available.emit(tab != -1)

    def set_default_path(self, path):
        self.default_path = path

    def populate_groups(self):
        self.filterGroupComboBox.clear()
        self.filterGroupComboBox.addItem('')
        for g in sorted(self.groups[self.filterTypeComboBox.currentText()]):
            self.filterGroupComboBox.addItem(g)

    def setupUi(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_file)
        self.tabs.currentChanged.connect(self._current_editor_changed)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)

        self.find_widget = FindReplace(self, enable_replace=True)
        self.find_widget.hide()

        self.content_widget = QWidget()
        layout = QGridLayout(self.content_widget)
        layout.addWidget(self.tabs)
        layout.addWidget(self.find_widget)

        self.setWidget(self.content_widget)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                p = url.toString()
                if p.startswith('file://') and p.endswith('.py'):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            p = url.toString()
            if p.startswith('file://') and p.endswith('.py'):
                self.add_file(p[7:])
        event.acceptProposedAction()

    def _setup_editor(self):
        font = QFont('Some font that does not exist')
        font.setStyleHint(font.TypeWriter, font.PreferDefault)
        editor = codeeditor.CodeEditor(self)
        try:
            editor.setup_editor(
                linenumbers=True, language='py',
                scrollflagarea=False,
                codecompletion_enter=self.enter_completion,
                tab_mode=False, edge_line=False, font=font,
                codecompletion_auto=True, go_to_definition=True,
                codecompletion_single=True, calltips=True)
        except TypeError:  # codecompletion_single is gone in 2.3.0
            editor.setup_editor(
                linenumbers=True, language='py',
                scrollflagarea=False,
                codecompletion_enter=self.enter_completion,
                tab_mode=False, edge_line=False, font=font,
                codecompletion_auto=True, go_to_definition=True,
                calltips=True)
        editor.setCursor(Qt.IBeamCursor)
        editor.horizontalScrollBar().setCursor(Qt.ArrowCursor)
        editor.verticalScrollBar().setCursor(Qt.ArrowCursor)
        return editor

    def _trigger_code_completion(self, automatic):
        editor = self.tabs.currentWidget()
        source_code = unicode(editor.toPlainText())
        offset = editor.get_position('cursor')
        text = editor.get_text('sol', 'cursor')

        if text.startswith('import '):
            comp_list = module_completion(text)
            words = text.split(' ')
            if ',' in words[-1]:
                words = words[-1].split(',')
            if comp_list:
                editor.show_completion_list(comp_list,
                                            completion_text=words[-1],
                                            automatic=automatic)
            return
        elif text.startswith('from '):
            comp_list = module_completion(text)
            words = text.split(' ')
            if '(' in words[-1]:
                words = words[:-2] + words[-1].split('(')
            if ',' in words[-1]:
                words = words[:-2] + words[-1].split(',')
            editor.show_completion_list(comp_list,
                                        completion_text=words[-1],
                                        automatic=automatic)
            return
        elif self.rope_project:
            textlist = self.rope_project.get_completion_list(
                source_code, offset, editor.file_name or self.rope_temp_path)
            if textlist:
                completion_text = re.split(r"[^a-zA-Z0-9_]", text)[-1]
                if text.lstrip().startswith('#') and text.endswith('.'):
                    return
                else:
                    editor.show_completion_list(textlist, completion_text,
                                                automatic)
                return

    def _trigger_calltip(self, position, auto=True):
        if not self.rope_project:
            return

        editor = self.tabs.currentWidget()
        source_code = unicode(editor.toPlainText())
        offset = position

        textlist = self.rope_project.get_calltip_text(
            source_code, offset, editor.file_name or self.rope_temp_path)
        if not textlist:
            return
        obj_fullname = ''
        signatures = []
        cts, doc_text = textlist
        cts = cts.replace('.__init__', '')
        parpos = cts.find('(')
        if parpos:
            obj_fullname = cts[:parpos]
            obj_name = obj_fullname.split('.')[-1]
            cts = cts.replace(obj_fullname, obj_name)
            signatures = [cts]
            if '()' in cts:
                # Either inspected object has no argument, or it's
                # a builtin or an extension -- in this last case
                # the following attempt may succeed:
                signatures = getsignaturesfromtext(doc_text, obj_name)
        if not obj_fullname:
            obj_fullname = codeeditor.get_primary_at(source_code, offset)
        if obj_fullname and not obj_fullname.startswith('self.') and doc_text:
            if signatures:
                signature = signatures[0]
                module = obj_fullname.split('.')[0]
                note = '\n    Function of %s module\n\n' % module
                text = signature + note + doc_text
            else:
                text = doc_text
            editor.show_calltip(obj_fullname, text, at_position=position)

    def _go_to_definition(self, position):
        if not self.rope_project:
            return

        editor = self.tabs.currentWidget()
        source_code = unicode(editor.toPlainText())
        offset = position
        fname, lineno = self.rope_project.get_definition_location(
            source_code, offset, editor.file_name or self.rope_temp_path)
        self.show_position(fname, lineno)

    def show_position(self, file_name, line):
        if not file_name or file_name == '<console>':
            return
        if not self.add_file(file_name):
            return
        if line is None:
            return

        editor = self.tabs.currentWidget()
        cursor = editor.textCursor()
        cursor.setPosition(0, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor,
                            line - 1)
        editor.setTextCursor(cursor)
        editor.raise_()
        editor.setFocus()
        self.raise_()

    def _finalize_new_editor(self, editor, tab_name):
        editor.file_was_changed = False
        editor.textChanged.connect(lambda: self._file_changed(editor))
        self.connect(editor, SIGNAL('trigger_code_completion(bool)'),
                     self._trigger_code_completion)
        self.connect(editor, SIGNAL('trigger_calltip(int)'),
                     self._trigger_calltip)
        self.connect(editor, SIGNAL("go_to_definition(int)"),
                     self._go_to_definition)

        self.tabs.addTab(editor, tab_name)
        self.tabs.setCurrentWidget(editor)

        self.setVisible(True)
        self.raise_()

    def new_file(self):
        editor = self._setup_editor()
        editor.file_name = None
        editor.set_text(self.template_code)
        self._finalize_new_editor(editor, '*New Plugin')

    def add_file(self, file_name):
        if file_name and not file_name.endswith('py'):
            QMessageBox.warning(self, 'Cannot load file',
                                'Only Python files are supported for editing')
            return False

        for i in xrange(self.tabs.count()):
            if file_name == self.tabs.widget(i).file_name:
                self.tabs.setCurrentIndex(i)
                self.raise_()
                return True

        editor = self._setup_editor()
        editor.file_name = file_name
        editor.set_text_from_file(file_name, 'python')

        # Remove extra newline
        text = editor.toPlainText()
        if text.endswith('\n'):
            editor.setPlainText(text[:-1])

        tab_name = os.path.split(file_name.decode('utf-8'))[1]
        self._finalize_new_editor(editor, tab_name)
        return True

    def close_file(self, tab_index):
        if self.tabs.widget(tab_index).file_was_changed and \
                self.tabs.widget(tab_index).file_name:
            fname = os.path.split(self.tabs.widget(tab_index).file_name)[1]
            if not fname:
                fname = 'New Plugin'
            ans = QMessageBox.question(
                self, 'File was changed',
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

    def get_editor(self, file_name):
        """ Get editor object for a file name. Returns None if no editor
        for the given file name exists.
        """
        for i in xrange(self.tabs.count()):
            if file_name == self.tabs.widget(i).file_name:
                return self.tabs.widget(i)
        return None

    def file_was_changed(self, editor):
        """ Returns if the file for an editor object has been changed.
        """
        if not editor:
            return False
        return editor.file_was_changed

    def _file_changed(self, editor):
        editor.file_was_changed = True

        if not editor.file_name:
            fname = 'New Plugin'
        else:
            fname = os.path.split(editor.file_name)[1]

        text = '*' + fname

        self.tabs.setTabText(self.tabs.indexOf(editor), text)

    def code(self, editor=None):
        """ Returns code for an editor object as a list of strings (one
        for each line).
        """
        if editor is None:
            editor = self.tabs.currentWidget()
        return [editor.get_text_line(l)
                for l in xrange(editor.get_line_count())]

    def code_has_errors(self, editor=None):
        """ Returns if the code from an editor object can be compiled.
        """
        code = '\n'.join(self.code(editor)).encode('UTF-8')
        try:
            compile(code, '<filter>', 'exec')
        except SyntaxError as e:
            return e.msg + ' (Line %d)' % (e.lineno)
        return None

    def save_file(self, editor, force_dialog=False):
        """ Save the file from an editor object.

        :param editor: The editor for which the while should be saved.
        :param bool force_dialog: If True, a "Save as..." dialog will be
            shown even if a file name is associated with the editor.
        """
        if not editor:
            return

        if force_dialog or not editor.file_name:
            d = QFileDialog(
                self, 'Choose where to save file',
                self.tabs.currentWidget().file_name or self.default_path)
            d.setAcceptMode(QFileDialog.AcceptSave)
            d.setNameFilter("Python files (*.py)")
            d.setDefaultSuffix('py')
            if d.exec_():
                file_name = unicode(d.selectedFiles()[0])
            else:
                return False
        else:
            file_name = editor.file_name

        err = self.code_has_errors(editor)
        if err:
            if QMessageBox.warning(
                    self, 'Error saving "%s"' % editor.file_name,
                    'Compile error:\n' + err + '\n\nIf this file contains '
                    'a plugin, it will disappear from the plugin list.\n'
                    'Save anyway?',
                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return False

        try:
            f = open(file_name, 'w')
            f.write('\n'.join(self.code(editor)).encode('UTF-8'))
            f.close()
        except IOError, e:
            QMessageBox.critical(
                self, 'Error saving "%s"' % editor.file_name, str(e))
            return False

        editor.file_name = file_name
        editor.file_was_changed = False
        fname = os.path.split(editor.file_name)[1]
        self.tabs.setTabText(self.tabs.indexOf(editor), fname)
        self.plugin_saved.emit(editor.file_name)
        return True

    def save_current(self, force_dialog=False):
        editor = self.tabs.currentWidget()
        self.save_file(editor, force_dialog)

    def _current_editor_changed(self, index):
        editor = self.tabs.widget(index)
        self.find_widget.set_editor(editor)
