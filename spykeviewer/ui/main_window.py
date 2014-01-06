import os
import sys
import json
import re
import traceback
import logging
import webbrowser
import copy
import pickle
import platform
import subprocess
import time

from PyQt4.QtGui import (QMainWindow, QMessageBox,
                         QApplication, QFileDialog, QInputDialog,
                         QLineEdit, QMenu, QDrag, QPainter, QPen,
                         QPalette, QDesktopServices, QFont,
                         QPixmap, QFileSystemModel, QHeaderView,
                         QActionGroup, QDockWidget)
from PyQt4.QtCore import (Qt, pyqtSignature, SIGNAL, QMimeData, QTimer,
                          QSettings, QCoreApplication, QUrl)

from spyderlib.widgets.internalshell import InternalShell
from spyderlib.widgets.externalshell.namespacebrowser import NamespaceBrowser
from spyderlib.widgets.sourcecode.codeeditor import CodeEditor
from spyderlib.utils.misc import get_error_match

import spykeutils
from spykeutils.plugin.data_provider import DataProvider
from spykeutils.plugin.analysis_plugin import AnalysisPlugin
from spykeutils.progress_indicator import CancelException
from spykeutils import SpykeException
from spykeutils.plot.helper import ProgressIndicatorDialog

from .. import api
from main_ui import Ui_MainWindow
from settings import SettingsWindow
from filter_dock import FilterDock
from filter_dialog import FilterDialog
from filter_group_dialog import FilterGroupDialog
from plugin_editor_dock import PluginEditorDock
import ipython_connection as ipy
from plugin_model import PluginModel
from remote_thread import RemoteThread


logger = logging.getLogger('spykeviewer')


# Monkeypatch variable editor
from spyderlib.widgets.dicteditor import DictDelegate
_orig_createEditor = DictDelegate.createEditor


def _patched_createEditor(*args, **kwargs):
    try:
        return _orig_createEditor(*args, **kwargs)
    except Exception:
        QMessageBox.critical(None, 'Edit item',
                             'Could not create editor for selected data!')

DictDelegate.createEditor = _patched_createEditor


#noinspection PyCallByClass,PyTypeChecker,PyArgumentList
class MainWindow(QMainWindow, Ui_MainWindow):
    """ The main window of Spyke Viewer.
    """

    def __init__(self, parent=None, splash=None):
        QMainWindow.__init__(self, parent)

        api.window = self
        self.splash = splash
        self.update_splash_screen('Creating user interface....')

        QCoreApplication.setOrganizationName('SpykeUtils')
        QCoreApplication.setApplicationName('Spyke Viewer')
        self.data_path = QDesktopServices.storageLocation(
            QDesktopServices.DataLocation)
        self.startup_script = os.path.join(self.data_path, 'startup.py')

        self.setupUi(self)
        self.dir = os.getcwd()

        # Threads providing output from remotely started plugins
        self.process_threads = {}
        self.remote_process_counter = 0
        QTimer.singleShot(1000, self.clean_finished_process_threads)

        # Lazy load mode menu
        self.load_actions = QActionGroup(self)
        self.load_actions.setExclusive(True)
        self.actionFull_Load.setActionGroup(self.load_actions)
        self.actionLazy_Load.setActionGroup(self.load_actions)
        self.actionCached_Lazy_Load.setActionGroup(self.load_actions)

        # Cascading mode menu
        self.cascade_actions = QActionGroup(self)
        self.cascade_actions.setExclusive(True)
        self.actionFull.setActionGroup(self.cascade_actions)
        self.actionLazy.setActionGroup(self.cascade_actions)

        # Python console
        self.console = None
        self.progress = ProgressIndicatorDialog(self)
        self.provider_factory = DataProvider
        self.selections = []
        self.provider = None
        self.plugin_paths = []
        self.init_python()

        # IPython menu option
        self.ipy_kernel = None
        if ipy.ipython_available:
            self.ipyDock = QDockWidget()
            self.ipyDock.setObjectName('ipythonDock')
            self.ipyDock.setWindowTitle('IPython')
            self.addDockWidget(Qt.BottomDockWidgetArea, self.ipyDock)
            self.ipyDock.setVisible(False)
            self.ipyDock.visibilityChanged.connect(self.on_ipyDock_visibilityChanged)

        # Drag and Drop for selections menu
        self.menuSelections.setAcceptDrops(True)
        self.menuSelections.paintEvent =\
            self.on_menuSelections_paint
        self.menuSelections.mousePressEvent =\
            self.on_menuSelections_mousePressed
        self.menuSelections.mouseMoveEvent =\
            self.on_menuSelections_mouseMoved
        self.menuSelections.dragEnterEvent =\
            self.on_menuSelections_dragEnter
        self.menuSelections.dragMoveEvent =\
            self.on_menuSelections_dragMoved
        self.menuSelections.dropEvent =\
            self.on_menuSelections_drop

        self.seldrag_start_pos = None
        self.seldrag_selection = None
        self.seldrag_target = None
        self.seldrag_target_upper = False

        # Filters
        settings = QSettings()
        if not settings.contains('filterPath'):
            data_path = QDesktopServices.storageLocation(
                QDesktopServices.DataLocation)
            self.filter_path = os.path.join(data_path, 'filters')
        else:
            self.filter_path = settings.value('filterPath')

        filter_types = self.get_filter_types()

        self.filterDock = FilterDock(self.filter_path, filter_types,
                                     menu=self.menuFilter, parent=self)
        self.filterDock.setObjectName('filterDock')
        self.filterDock.current_filter_changed.connect(
            self.on_current_filter_changed)
        self.filterDock.filters_changed.connect(
            self.on_filters_changed)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filterDock)

        self.show_filter_exceptions = True

        # Plugins
        self.menuPluginsContext = QMenu(self)
        self.menuPluginsContext.addAction(self.actionRunPlugin)
        self.menuPluginsContext.addAction(self.actionRemotePlugin)
        self.menuPluginsContext.addAction(self.actionConfigurePlugin)
        self.menuPluginsContext.addAction(self.actionEditPlugin)
        self.menuPluginsContext.addAction(self.actionShowPluginFolder)

        # Plugin Editor
        self.pluginEditorDock = PluginEditorDock()
        self.pluginEditorDock.setObjectName('editorDock')
        self.addDockWidget(Qt.RightDockWidgetArea, self.pluginEditorDock)
        self.pluginEditorDock.setVisible(False)
        self.pluginEditorDock.plugin_saved.connect(self.plugin_saved)
        self.pluginEditorDock.file_available.connect(self.on_file_available)

        self.consoleDock.edit_script = lambda (path): \
            self.pluginEditorDock.add_file(path)

        def p(x):
            match = get_error_match(unicode(x))
            if match:
                fname, lnb = match.groups()
                self.pluginEditorDock.show_position(fname, int(lnb))

        self.connect(self.console, SIGNAL("go_to_error(QString)"), p)

        # File navigation
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath('')
        self.fileTreeView.setModel(self.file_system_model)
        self.fileTreeView.setCurrentIndex(
            self.file_system_model.index(self.dir))
        self.fileTreeView.expand(self.file_system_model.index(self.dir))

        self.fileTreeView.setColumnHidden(1, True)
        self.fileTreeView.setColumnHidden(2, True)
        self.fileTreeView.setColumnHidden(3, True)

        self.fileTreeView.header().setResizeMode(QHeaderView.ResizeToContents)

        # Docks
        self.setCentralWidget(None)

        # Finish initialization if we are not a subclass
        if type(self) is MainWindow:
            self.finish_initialization()

    ##### Startup ########################################################
    def update_splash_screen(self, message):
        if not self.splash:
            return

        self.splash.showMessage(message, Qt.AlignCenter | Qt.AlignBottom)
        self.splash.show()
        QCoreApplication.processEvents()

    def finish_initialization(self):
        """ This should to be called at the end of the initialization phase
        of the program (e.g. at the end of the ``__init__()`` method of a
        domain-specific subclass).
        """
        self.update_view_menu()

        self.update_splash_screen('Restoring saved state...')
        self.restore_state()

        self.update_splash_screen('Running startup script...')
        self.run_startup_script()
        self.set_config_options()

        if api.config.load_mode == 1:
            self.actionLazy_Load.trigger()
        elif api.config.load_mode == 2:
            self.actionCached_Lazy_Load.trigger()
        else:
            self.actionFull_Load.trigger()

        if api.config.lazy_cascading:
            self.actionLazy.trigger()
        else:
            self.actionFull.trigger()

        self.update_splash_screen('Loading plugins...')
        self.reload_plugins()
        self.load_plugin_configs()

        if api.config.load_selection_on_start:
            self.update_splash_screen('Loading previous selection...')
            self.load_current_selection()

    def get_filter_types(self):
        """ Return a list of filter type tuples as required by
            :class:`filter_dock.FilterDock. Override in domain-specific
            subclass.
        """
        return []

    def update_view_menu(self):
        """ Recreate the "View" menu.
        """
        if hasattr(self, 'menuView'):
            a = self.menuView.menuAction()
            self.mainMenu.removeAction(a)
            self.menuView.clear()
        self.menuView = self.createPopupMenu()
        self.menuView.setTitle('&View')
        self.mainMenu.insertMenu(self.menuHelp.menuAction(), self.menuView)

    def set_default_plugin_path(self):
        """ Set the default plugin path (contains the standard plugins
        after installation).
        """
        if hasattr(sys, 'frozen'):
            module_path = os.path.dirname(sys.executable)
        else:
            file_path = os.path.abspath(os.path.dirname(__file__))
            module_path = os.path.dirname(file_path)
        plugin_path = os.path.join(module_path, 'plugins')

        if os.path.isdir(plugin_path):
            self.plugin_paths.append(plugin_path)
        else:
            logger.warning('Plugin path "%s" does not exist, no plugin '
                           'path set!' %
                           plugin_path)

    def restore_state(self):
        """ Restore previous state of the GUI and settings from saved
        configuration.
        """
        settings = QSettings()
        if not settings.contains('windowGeometry') or \
                not settings.contains('windowState'):
            self.set_initial_layout()
        else:
            self.restoreGeometry(settings.value('windowGeometry'))
            self.restoreState(settings.value('windowState'))

        if not settings.contains('pluginPaths'):
            self.set_default_plugin_path()
        else:
            paths = settings.value('pluginPaths')
            self.plugin_paths = []
            if paths is not None:
                for p in paths:
                    if not os.path.isdir(p):
                        logger.warning('Plugin path "%s" does not exist, '
                                       'removing from configuration...' % p)
                    else:
                        self.plugin_paths.append(p)
            
            if not self.plugin_paths:
                logger.warning('No plugin paths set! Setting default path...')
                self.set_default_plugin_path()

        if not settings.contains('selectionPath'):
            self.selection_path = os.path.join(self.data_path, 'selections')
        else:
            self.selection_path = settings.value('selectionPath')

        if not settings.contains('dataPath'):
            AnalysisPlugin.data_dir = os.path.join(self.data_path, 'data')
        else:
            AnalysisPlugin.data_dir = settings.value('dataPath')

        if not settings.contains('remoteScript') or not os.path.isfile(
                settings.value('remoteScript')):
            if settings.contains('remoteScript'):
                logger.warning('Remote script not found! Reverting to '
                               'default location...')
            if hasattr(sys, 'frozen'):
                path = os.path.dirname(sys.executable)
            else:
                path = os.path.dirname(spykeutils.__file__)
                path = os.path.join(os.path.abspath(path), 'plugin')
            self.remote_script = os.path.join(path, 'startplugin.py')
        else:
            self.remote_script = settings.value('remoteScript')

        if self.plugin_paths:
            self.pluginEditorDock.set_default_path(self.plugin_paths[-1])

    def set_initial_layout(self):
        """ Set an initial layout for the docks (when no previous
        configuration could be loaded).
        """
        self.filesDock.setMinimumSize(100, 100)
        self.resize(800, 750)

        self.removeDockWidget(self.filesDock)
        self.removeDockWidget(self.filterDock)
        self.removeDockWidget(self.pluginDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filesDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filterDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.pluginDock)
        self.tabifyDockWidget(self.filterDock, self.pluginDock)
        self.filesDock.setVisible(True)
        self.filterDock.setVisible(True)
        self.pluginDock.setVisible(True)

        self.consoleDock.setVisible(False)
        self.variableExplorerDock.setVisible(False)
        self.historyDock.setVisible(False)
        self.tabifyDockWidget(self.consoleDock, self.variableExplorerDock)
        self.tabifyDockWidget(self.variableExplorerDock, self.historyDock)

    def run_startup_script(self):
        """ Run the startup script that can be used for configuration.
        """
        if not os.path.isfile(self.startup_script):
            content = ('# Startup script for Spyke Viewer\n'
                       'import spykeviewer.api as spyke')
            try:
                path = os.path.dirname(self.startup_script)
                if not os.path.isdir(path):
                    os.makedirs(path)

                with open(self.startup_script, 'w') as f:
                    f.write(content)
            except:
                logger.warning('Could not create startup script ' +
                               self.startup_script + ':\n' +
                               traceback.format_exc() + '\n')
                return

        try:
            with open(self.startup_script, 'r') as f:
                # We turn all encodings to UTF-8, so remove encoding
                # comments manually
                lines = f.readlines()
                if lines:
                    if re.findall('coding[:=]\s*([-\w.]+)', lines[0]):
                        lines.pop(0)
                    elif re.findall('coding[:=]\s*([-\w.]+)', lines[1]):
                        lines.pop(1)
                    source = ''.join(lines).decode('utf-8')
                    code = compile(source, self.startup_script, 'exec')
                    exec(code, {})
        except Exception:
            logger.warning('Error during execution of startup script ' +
                           self.startup_script + ':\n' +
                           traceback.format_exc() + '\n')

    def set_config_options(self):
        self.console.set_codecompletion_enter(
            api.config.codecomplete_console_enter)
        self.pluginEditorDock.enter_completion = \
            api.config.codecomplete_editor_enter

    ##### Interactive Python #############################################
    def get_console_objects(self):
        """ Return a dictionary of objects that should be included in the
        console on startup. These objects will also not be displayed in
        variable explorer. Override this function in domain-specific
        subclasses, e.g. for imports.
        """
        import numpy
        import scipy
        import matplotlib.pyplot as plt
        import guiqwt.pyplot as guiplt
        plt.ion()
        guiplt.ion()

        return {'np': numpy, 'sp': scipy, 'plt': plt, 'guiplt': guiplt,
                'spyke': api}

    def init_python(self):
        """ Initialize the Python docks: console, history and variable
        explorer.
        """
        class StreamDuplicator():
            def __init__(self, out_list):
                self.outs = out_list

            def write(self, s):
                for o in self.outs:
                    o.write(s)

            def flush(self):
                for o in self.outs:
                    if hasattr(o, 'flush'):
                        o.flush()

            def set_parent(self, _):  # Called when connecting IPython 0.13
                pass

        # Fixing bugs in the internal shell
        class FixedInternalShell(InternalShell):
            def __init__(self, *args, **kwargs):
                super(FixedInternalShell, self).__init__(*args, **kwargs)

            # Do not try to show a completion list when completions is None
            def show_completion_list(self, completions, completion_text="",
                                     automatic=True):
                if completions is None:
                    return
                super(FixedInternalShell, self).show_completion_list(
                    completions, completion_text, automatic)

            # Do not get dir() for non-text objects
            def get_dir(self, objtxt):
                if not isinstance(objtxt, (str, unicode)):
                    return
                return super(FixedInternalShell, self).get_dir(objtxt)

            # Fix exception when using non-ascii characters
            def run_command(self, cmd, history=True, new_prompt=True):
                """Run command in interpreter"""
                if not cmd:
                    cmd = ''
                else:
                    if history:
                        self.add_to_history(cmd)
                cmd_line = cmd + '\n'
                self.interpreter.stdin_write.write(cmd_line.encode('utf-8'))
                if not self.multithreaded:
                    self.interpreter.run_line()
                    self.emit(SIGNAL("refresh()"))

        # Console
        msg = ('current and selections can be used to access selected data'
               '\n\nModules imported at startup: ')
        ns = self.get_console_objects()
        excludes = ['execfile', 'guiplt', 'help', 'raw_input', 'runfile']
        first_item = True
        for n, o in ns.iteritems():
            if type(o) == type(sys):
                if not first_item:
                    msg += ', '
                first_item = False
                msg += o.__name__
                if n != o.__name__:
                    msg += ' as ' + n

                excludes.append(n)

        ns['current'] = self.provider
        ns['selections'] = self.selections

        font = QFont("Monospace")
        font.setStyleHint(font.TypeWriter, font.PreferDefault)
        if not platform.system() == 'Darwin':
            font.setPointSize(9)
        self.console = FixedInternalShell(
            self.consoleDock, namespace=ns, multithreaded=False,
            message=msg, max_line_count=10000, font=font)
        #self.console.clear_terminal()

        self.console.set_codecompletion_auto(True)
        self.console.set_calltips(True)
        self.console.setup_calltips(size=600, font=font)
        self.console.setup_completion(size=(370, 240), font=font)

        self.consoleDock.setWidget(self.console)

        # Variable browser
        self.browser = NamespaceBrowser(self.variableExplorerDock)
        self.browser.set_shellwidget(self.console)
        self.browser.setup(
            check_all=True, exclude_private=True,
            exclude_uppercase=False, exclude_capitalized=False,
            exclude_unsupported=False, truncate=False, minmax=False,
            collvalue=False, remote_editing=False, inplace=False,
            autorefresh=False,
            excluded_names=excludes)
        self.variableExplorerDock.setWidget(self.browser)

        # History
        self.history = CodeEditor(self.historyDock)
        self.history.setup_editor(linenumbers=False, language='py',
                                  scrollflagarea=False)
        self.history.setReadOnly(True)
        self.history.set_text('\n'.join(self.console.history))
        self.history.set_cursor_position('eof')
        self.historyDock.setWidget(self.history)
        self.console.connect(self.console, SIGNAL("refresh()"),
                             self._append_python_history)

        # Duplicate stdout and stderr for console
        # Not using previous stdout, only stderr. Using StreamDuplicator
        # because spyder stream does not have flush() method...
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        logger.addHandler(ch)

        sys.stdout = StreamDuplicator([sys.stdout])
        sys.stderr = StreamDuplicator([sys.stderr, sys.__stderr__])

    def _append_python_history(self):
        self.browser.refresh_table()
        self.history.append('\n' + self.console.history[-1])
        self.history.set_cursor_position('eof')

    def on_ipyDock_visibilityChanged(self, visible):
        if visible and not self.ipyDock.widget():
            self.create_ipython_kernel()
            widget = self.ipy_kernel.get_widget()
            self.ipyDock.setWidget(widget)

    def create_ipython_kernel(self):
        """ Create a new IPython kernel. Does nothing if a kernel already
        exists.
        """
        if not ipy.ipython_available or self.ipy_kernel:
            return

        self.ipy_kernel = ipy.IPythonConnection()
        self.ipy_kernel.push({'current': self.provider,
                              'selections': self.selections})

    def on_variableExplorerDock_visibilityChanged(self, visible):
        if visible:
            self.browser.refresh_table()

    def on_historyDock_visibilityChanged(self, visible):
        if visible:
            self.history.set_cursor_position('eof')

    ##### Selections #####################################################
    def on_menuSelections_mousePressed(self, event):
        if event.button() == Qt.LeftButton:
            action = self.menuSelections.actionAt(event.pos())
            if action:
                selection = action.data()
                if selection:
                    self.seldrag_start_pos = event.pos()
                    self.seldrag_selection = selection
        else:
            self.seldrag_start_pos = None
            self.seldrag_selection = None
            self.seldrag_target = None
        QMenu.mousePressEvent(self.menuSelections, event)

    def on_menuSelections_mouseMoved(self, event):
        if event.buttons() & Qt.LeftButton and self.seldrag_start_pos:
            if ((event.pos() - self.seldrag_start_pos).manhattanLength() >=
                    QApplication.startDragDistance()):
                drag = QDrag(self.menuSelections)
                data = QMimeData()
                data.setText(self.seldrag_selection.name)
                drag.setMimeData(data)
                drag.exec_()
                self.seldrag_start_pos = None
                self.seldrag_selection = None
                self.seldrag_target = None
        QMenu.mouseMoveEvent(self.menuSelections, event)

    def on_menuSelections_paint(self, event):
        QMenu.paintEvent(self.menuSelections, event)
        if self.seldrag_target:
            # Paint line where selection will be dropped
            p = QPainter()
            color = QPalette().color(self.menuSelections.foregroundRole())
            pen = QPen(color, 2, Qt.SolidLine)
            p.begin(self.menuSelections)
            p.setPen(pen)
            rect = self.menuSelections.actionGeometry(self.seldrag_target)
            if self.seldrag_target_upper:
                p.drawLine(rect.topLeft(), rect.topRight())
            else:
                p.drawLine(rect.bottomLeft(), rect.bottomRight())
            p.end()

    def _menuSelections_pos_is_drop_target(self, pos):
        """ Return if selection can be dropped at this position and
            prepare information needed for drawing and dropping
        """
        action = self.menuSelections.actionAt(pos)
        if not action or not action.data():
            self.seldrag_target = None
            return False

        self.seldrag_target = action
        rect = self.menuSelections.actionGeometry(action)
        if pos.y() < rect.top() + rect.height() / 2:
            self.seldrag_target_upper = True
        else:
            self.seldrag_target_upper = False
        return True

    def on_menuSelections_dragEnter(self, event):
        event.setDropAction(Qt.MoveAction)
        if self._menuSelections_pos_is_drop_target(event.pos()):
            event.accept()
        else:
            event.ignore()

        QMenu.dragEnterEvent(self.menuSelections, event)

    def on_menuSelections_dragMoved(self, event):
        event.setDropAction(Qt.MoveAction)
        if self._menuSelections_pos_is_drop_target(event.pos()):
            event.accept()
            self.menuSelections.update()
        else:
            event.ignore()

        QMenu.dragMoveEvent(self.menuSelections, event)

    def on_menuSelections_drop(self, event):
        source = self.seldrag_selection
        target = self.seldrag_target.data()
        if source != target:
            self.selections.remove(source)
            target_index = self.selections.index(target)
            if not self.seldrag_target_upper:
                target_index += 1
            self.selections.insert(target_index, source)
            self.populate_selection_menu()

        QMenu.dropEvent(self.menuSelections, event)

    def populate_selection_menu(self):
        self.menuSelections.clear()
        a = self.menuSelections.addAction('New')
        a.triggered.connect(self.on_selection_new)
        a = self.menuSelections.addAction('Clear')
        a.triggered.connect(self.on_selection_clear)
        self.menuSelections.addSeparator()

        for i, s in enumerate(self.selections):
            m = self.menuSelections.addMenu(s.name)
            m.menuAction().setData(s)

            a = m.addAction('Load')
            self.connect(a, SIGNAL('triggered()'),
                         lambda sel=s: self.on_selection_load(sel))

            a = m.addAction('Save')
            self.connect(a, SIGNAL('triggered()'),
                         lambda sel=s: self.on_selection_save(sel))

            a = m.addAction('Rename')
            self.connect(a, SIGNAL('triggered()'),
                         lambda sel=s: self.on_selection_rename(sel))

            a = m.addAction('Remove')
            self.connect(a, SIGNAL('triggered()'),
                         lambda sel=s: self.on_selection_remove(sel))

    def on_selection_load(self, selection):
        self.set_current_selection(selection.data_dict())

    def on_selection_save(self, selection):
        i = self.selections.index(selection)
        self.selections[i] = self.provider_factory(
            self.selections[i].name, self)
        self.populate_selection_menu()

    def on_selection_clear(self):
        if QMessageBox.question(
            self, 'Please confirm',
            'Do you really want to remove all selections?',
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        del self.selections[:]
        self.populate_selection_menu()

    def on_selection_rename(self, selection):
        (name, ok) = QInputDialog.getText(
            self, 'Edit selection name',
            'New name:', QLineEdit.Normal, selection.name)
        if ok and name:
            selection.name = name
            self.populate_selection_menu()

    def on_selection_remove(self, selection):
        if QMessageBox.question(
                self, 'Please confirm',
                'Do you really want to remove the selection "%s"?' %
                selection.name,
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        self.selections.remove(selection)
        self.populate_selection_menu()

    def on_selection_new(self):
        self.selections.append(self.provider_factory(
            'Selection %d' % (len(self.selections) + 1), self))
        self.populate_selection_menu()

    def serialize_selections(self):
        sl = list()  # Selection list, current selection as first item
        sl.append(self.provider_factory('__current__', self).data_dict())
        for s in self.selections:
            sl.append(s.data_dict())
        return json.dumps(sl, sort_keys=True, indent=2)

    def save_selections_to_file(self, filename):
        f = open(filename, 'w')
        f.write(self.serialize_selections())
        f.close()

    def load_selections_from_file(self, filename):
        try:
            f = open(filename, 'r')
            p = json.load(f)
            f.close()
            for s in p:
                if not s:
                    continue
                if s['name'] == '__current__':
                    self.set_current_selection(s)
                else:
                    self.add_selection(s)
        except Exception, e:
            QMessageBox.critical(self, 'Error loading selection',
                                 str(e).decode('utf8'))
            logger.warning('Error loading selection:\n' +
                           traceback.format_exc() + '\n')
        finally:
            self.progress.done()
            self.populate_selection_menu()

    def load_current_selection(self):
        """ Load the displayed (current) selection from a file.
        """
        current_selection = os.path.join(
            self.selection_path, '.current.sel')
        if os.path.isfile(current_selection):
            self.load_selections_from_file(current_selection)
        else:
            self.populate_selection_menu()

    @pyqtSignature("")
    def on_actionSave_selection_triggered(self):
        d = QFileDialog(self, 'Choose where to save selection',
                        self.selection_path)
        d.setAcceptMode(QFileDialog.AcceptSave)
        d.setNameFilter("Selection files (*.sel)")
        d.setDefaultSuffix('sel')
        if d.exec_():
            filename = str(d.selectedFiles()[0])
        else:
            return

        self.save_selections_to_file(filename)

    @pyqtSignature("")
    def on_actionLoad_selection_triggered(self):
        d = QFileDialog(self, 'Choose selection file',
                        self.selection_path)
        d.setAcceptMode(QFileDialog.AcceptOpen)
        d.setFileMode(QFileDialog.ExistingFile)
        d.setNameFilter("Selection files (*.sel)")
        if d.exec_():
            filename = unicode(d.selectedFiles()[0])
        else:
            return

        self.load_selections_from_file(filename)

    def set_current_selection(self, data):
        """ Set the current selection based on a dictionary of selection
        data. Override in domain-specific subclasses.
        """
        raise NotImplementedError('No selection model defined!')

    def add_selection(self, data):
        """ Add a selection based on a dictionary of selection data.
        Override in domain-specific subclasses.
        """
        raise NotImplementedError('No selection model defined!')

    ##### Filters ########################################################
    def on_current_filter_changed(self):
        enabled = self.filterDock.current_is_data_item()
        self.actionEditFilter.setEnabled(enabled)
        self.actionDeleteFilter.setEnabled(enabled)
        self.actionCopyFilter.setEnabled(enabled)

    def on_filters_changed(self, filter_type):
        self.filter_populate_function[filter_type]()

    def editFilter(self, copy_item):
        top = self.filterDock.current_filter_type()
        group = self.filterDock.current_filter_group()
        name = self.filterDock.current_name()
        item = self.filterDock.current_item()

        group_filters = None
        if not self.filterDock.is_current_group():
            dialog = FilterDialog(
                self.filterDock.filter_group_dict(), top, group, name,
                item.code, item.combined, item.on_exception, self)
        else:
            group_filters = self.filterDock.group_filters(top, name)
            group = None
            dialog = FilterGroupDialog(top, name, item.exclusive, self)

        while dialog.exec_():
            if copy_item and name == dialog.name():
                QMessageBox.critical(
                    self, 'Error saving',
                    'Please select a different name for the copied element')
                continue
            try:
                if not copy_item and name != dialog.name():
                    self.filterDock.delete_item(top, name, group)
                if not self.filterDock.is_current_group():
                    self.filterDock.add_filter(
                        dialog.name(), dialog.group(), dialog.type(),
                        dialog.code(), dialog.on_exception(),
                        dialog.combined(), overwrite=True)
                else:
                    self.filterDock.add_filter_group(
                        dialog.name(), dialog.type(), dialog.exclusive(),
                        copy.deepcopy(group_filters), overwrite=True)
                break
            except ValueError as e:
                QMessageBox.critical(self, 'Error saving', str(e))

    def get_active_filters(self, filter_type):
        """ Return a list of active filters for the selected filter type
        """
        return self.filterDock.get_active_filters(filter_type)

    def is_filtered(self, item, filters):
        """ Return if one of the filter functions in the given list
        applies to the given item. Combined filters are ignored.
        """
        for f, n in filters:
            if f.combined or not f.active:
                continue
            try:
                if not f.function()(item):
                    return True
            except Exception, e:
                if self.show_filter_exceptions:
                    sys.stderr.write(
                        'Exception in filter ' + n + ':\n' + str(e) + '\n')
                if not f.on_exception:
                    return True
        return False

    def filter_list(self, items, filters):
        """ Return a filtered list of the given list with the given filter
        functions. Only combined filters are used.
        """
        if not items:
            return items
        item_type = type(items[0])
        for f, n in filters:
            if not f.combined or not f.active:
                continue
            try:
                items = [i for i in f.function()(items)
                         if isinstance(i, item_type)]
            except Exception, e:
                if self.show_filter_exceptions:
                    sys.stderr.write(
                        'Exception in filter ' + n + ':\n' + str(e) + '\n')
                if not f.on_exception:
                    return []
        return items

    def refresh_filters(self):
        """ Refresh the list of possible filters. Call if filters are changed
        programmatically.
        """
        self.filterDock.populate_filter_tree()

    @pyqtSignature("")
    def on_actionNewFilterGroup_triggered(self):
        top = self.filterDock.current_filter_type()

        dialog = FilterGroupDialog(top, parent=self)
        while dialog.exec_():
            try:
                self.filterDock.add_filter_group(dialog.name(), dialog.type(),
                                                 dialog.exclusive())
                break
            except ValueError as e:
                QMessageBox.critical(self, 'Error creating group', str(e))

    @pyqtSignature("")
    def on_actionNewFilter_triggered(self):
        top = self.filterDock.current_filter_type()
        group = self.filterDock.current_filter_group()

        dialog = FilterDialog(self.filterDock.filter_group_dict(), type=top,
                              group=group, parent=self)
        while dialog.exec_():
            try:
                self.filterDock.add_filter(dialog.name(), dialog.group(),
                                           dialog.type(), dialog.code(),
                                           dialog.on_exception(),
                                           dialog.combined())
                break
            except ValueError as e:
                QMessageBox.critical(self, 'Error creating filter', str(e))

    @pyqtSignature("")
    def on_actionDeleteFilter_triggered(self):
        self.filterDock.delete_current_filter()

    @pyqtSignature("")
    def on_actionEditFilter_triggered(self):
        self.editFilter(False)

    @pyqtSignature("")
    def on_actionCopyFilter_triggered(self):
        self.editFilter(True)

    ##### Plugins ########################################################
    def get_plugin_configs(self):
        """ Return dictionary indexed by (name,path) tuples with configuration
        dictionaries for all plugins.
        """
        indices = self.plugin_model.get_all_indices()
        c = {}

        for idx in indices:
            path = self.plugin_model.data(
                idx, self.plugin_model.FilePathRole)
            plug = self.plugin_model.data(idx, self.plugin_model.DataRole)
            if plug:
                c[(plug.get_name(), path)] = plug.get_parameters()

        return c

    def set_plugin_configs(self, configs):
        """ Takes a dictionary indexed by plugin name with configuration
        dictionaries for plugins and sets configurations of plugins.
        """
        indices = self.plugin_model.get_all_indices()

        d = {}
        for idx in indices:
            path = self.plugin_model.data(
                idx, self.plugin_model.FilePathRole)
            plug = self.plugin_model.data(idx, self.plugin_model.DataRole)
            if plug:
                d[(plug.get_name(), path)] = plug

        for n, c in configs.iteritems():
            if n in d:
                d[n].set_parameters(c)

    def reload_plugins(self, keep_configs=True):
        """ Reloads all plugins.

        :param bool keep_configs: If ``True``, try to restore all plugin
            configuration parameters after reloading.
            Default: ``True``
        """
        old_closed = self._get_closed_folders()
        old_path = None
        old_configs = {}
        if hasattr(self, 'plugin_model'):
            if keep_configs:
                old_configs = self.get_plugin_configs()
            item = self.pluginsTreeView.currentIndex()
            if item:
                old_path = self.plugin_model.data(
                    item, self.plugin_model.FilePathRole)

        try:
            self.plugin_model = PluginModel()
            for p in self.plugin_paths:
                self.plugin_model.add_path(p)
        except Exception, e:
            QMessageBox.critical(self, 'Error loading plugins', str(e))
            return

        self.pluginsTreeView.setModel(self.plugin_model)

        selected_index = None
        if old_path:
            indices = self.plugin_model.get_indices_for_path(old_path)
            if indices:
                selected_index = indices[0]
                self.pluginsTreeView.setCurrentIndex(selected_index)
        self.pluginsTreeView.expandAll()
        self.pluginsTreeView.selectionModel().currentChanged.connect(
            self.selected_plugin_changed)
        self.selected_plugin_changed(selected_index)
        self.set_plugin_configs(old_configs)
        self.restore_closed_plugin_folders(old_closed)

    def _equal_path(self, index, path):
        path_list = list(reversed(path.split('/')))

        while index.row() >= 0:
            if not path_list or index.data() != path_list.pop(0):
                return False
            index = index.parent()
        return True

    def restore_closed_plugin_folders(self, paths):
        if paths is not None:
            folders = self.plugin_model.get_all_folders()
            for p in paths:
                for f in folders:
                    if self._equal_path(f, p):
                        self.pluginsTreeView.setExpanded(f, False)
                        break

    def load_plugin_configs(self, closed_folders=None):
        # Restore closed plugin folders
        paths = closed_folders
        if paths is None:
            settings = QSettings()
            if settings.contains('closedPluginFolders'):
                paths = settings.value('closedPluginFolders')
        self.restore_closed_plugin_folders(paths)

        # Restore plugin configurations
        configs_path = os.path.join(self.data_path, 'plugin_configs.p')
        if os.path.isfile(configs_path):
            with open(configs_path, 'r') as f:
                try:
                    configs = pickle.load(f)
                    self.set_plugin_configs(configs)
                except:
                    pass  # It does not matter if we can't load plugin configs

    def selected_plugin_changed(self, current):
        enabled = True
        if not current:
            enabled = False
        elif not self.plugin_model.data(current, Qt.UserRole):
            enabled = False

        self.actionRunPlugin.setEnabled(enabled)
        self.actionEditPlugin.setEnabled(enabled)
        self.actionConfigurePlugin.setEnabled(enabled)
        self.actionRemotePlugin.setEnabled(enabled)
        self.actionShowPluginFolder.setEnabled(enabled)

    @pyqtSignature("")
    def on_actionRunPlugin_triggered(self):
        plugin = self._save_plugin_before_run()
        if not plugin:
            return

        self._run_plugin(plugin)

    def _save_plugin_before_run(self):
        ana = self.current_plugin()
        if not ana:
            return None

        if api.config.save_plugin_before_starting:
            e = self.pluginEditorDock.get_editor(ana.source_file)
            if self.pluginEditorDock.file_was_changed(e):
                if not self.pluginEditorDock.save_file(e):
                    return None
                ana = self.current_plugin()
                if not ana:
                    return None
        return ana

    def _run_plugin(self, plugin, current=None, selections=None):
        if current is None:
            current = self.provider
        if selections is None:
            selections = self.selections
        try:
            return plugin.start(current, selections)
        except SpykeException, err:
            QMessageBox.critical(self, 'Error executing plugin', str(err))
        except CancelException:
            return None
        except Exception, e:
            # Only print stack trace from plugin on
            tb = sys.exc_info()[2]
            while not ('self' in tb.tb_frame.f_locals and
                       tb.tb_frame.f_locals['self'] == plugin):
                if tb.tb_next is not None:
                    tb = tb.tb_next
                else:
                    break
            traceback.print_exception(type(e), e, tb)
            return None
        finally:
            self.progress.done()

    @pyqtSignature("")
    def on_actionEditPlugin_triggered(self):
        item = self.pluginsTreeView.currentIndex()
        path = ''
        if item:
            path = self.plugin_model.data(
                item, self.plugin_model.FilePathRole)
        if not path and self.plugin_paths:
            path = self.plugin_paths[0]
        self.pluginEditorDock.add_file(path)

    @pyqtSignature("")
    def on_actionLoad_Python_File_triggered(self):
        path = ''
        if self.plugin_paths:
            path = self.plugin_paths[-1]
        d = QFileDialog(self, 'Choose file to edit', path)
        d.setAcceptMode(QFileDialog.AcceptOpen)
        d.setFileMode(QFileDialog.ExistingFiles)
        d.setNameFilter("Python files (*.py)")
        if not d.exec_():
            return

        for p in d.selectedFiles():
            self.pluginEditorDock.add_file(unicode(p))

    @pyqtSignature("")
    def on_actionConfigurePlugin_triggered(self):
        ana = self.current_plugin()
        if not ana:
            return

        ana.configure()

    @pyqtSignature("")
    def on_actionRefreshPlugins_triggered(self):
        self.reload_plugins()

    @pyqtSignature("")
    def on_actionNewPlugin_triggered(self):
        self.pluginEditorDock.new_file()

    @pyqtSignature("")
    def on_actionSavePlugin_triggered(self):
        self.pluginEditorDock.save_current()

    @pyqtSignature("")
    def on_actionSavePluginAs_triggered(self):
        self.pluginEditorDock.save_current(True)

    @pyqtSignature("")
    def on_actionShowPluginFolder_triggered(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(
            os.path.dirname(self.current_plugin_path())))

    @pyqtSignature("")
    def on_actionRemotePlugin_triggered(self):
        plugin = self._save_plugin_before_run()
        if not plugin:
            return

        self._execute_remote_plugin(plugin)

    def send_plugin_info(self, name, path, selections, config, io_files):
        """ Send information to start a plugin to the configured remote
        script.

        :param str name: Name of the plugin class
        :param str path: Path of the plugin file
        :param str selections: Serialized selections to use
        :param str config: Pickled plugin configuration
        :param list io_files: List of paths to required IO plugins.
        """
        # Save files to circumvent length limit for command line
        selection_path = os.path.join(
            self.selection_path, '.temp_%f_.sel' % time.time())
        with open(selection_path, 'w') as f:
            f.write(selections)

        params = ['python', self.remote_script,
                  name, path, selection_path, '-cf', '-sf',
                  '-c', config, '-dd', AnalysisPlugin.data_dir]
        if io_files:
            params.append('-io')
            params.extend(io_files)
        params.extend(api.config.remote_script_parameters)
        p = subprocess.Popen(
            params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std = RemoteThread(p, self.remote_process_counter, False, self)
        err = RemoteThread(p, self.remote_process_counter, True, self)
        self.connect(std, SIGNAL("output(int, QString)"), self.output_std)
        self.connect(err, SIGNAL("output(int, QString)"), self.output_err)
        self.connect(err, SIGNAL("execution_complete(int)"),
                     self.remote_plugin_done)
        std.start()
        err.start()
        self.process_threads[self.remote_process_counter] = (std, err, p)
        print '[#%d started]' % self.remote_process_counter
        self.remote_process_counter += 1

    def output_std(self, id_, line):
        print '[#%d]' % id_, line

    def output_err(self, id_, line):
        sys.stderr.write(line + '\n')

    def remote_plugin_done(self, id_):
        print '[#%d done]' % id_

    def clean_finished_process_threads(self):
        """ Periodically checks if threads for remote plugin output are
        still running, removes them otherwise.
        """
        for k in self.process_threads.keys():
            t = self.process_threads[k]
            if not t[0].isRunning() and not t[1].isRunning():
                t[2].wait()
                del self.process_threads[k]
        QTimer.singleShot(1000, self.clean_finished_process_threads)

    @pyqtSignature("")
    def on_actionEdit_Startup_Script_triggered(self):
        self.pluginEditorDock.add_file(self.startup_script)

    @pyqtSignature("")
    def on_actionRestorePluginConfigurations_triggered(self):
        self.reload_plugins(False)

    def on_pluginsTreeView_doubleClicked(self, index):
        self.on_actionRunPlugin_triggered()

    def on_pluginsTreeView_customContextMenuRequested(self, pos):
        self.menuPluginsContext.popup(self.pluginsTreeView.mapToGlobal(pos))

    def plugin_saved(self, path):
        if path == self.startup_script:
            return

        plugin_path = os.path.normpath(os.path.realpath(path))
        in_dirs = False
        for p in self.plugin_paths:
            directory = os.path.normpath(os.path.realpath(p))
            if os.path.commonprefix([plugin_path, directory]) == directory:
                in_dirs = True
                break

        if in_dirs:
            self.reload_plugins()
        elif api.config.ask_plugin_path:
            if QMessageBox.question(self, 'Warning',
                                    'The file "%s"' % plugin_path +
                                    ' is not in the currently valid plugin '
                                    'directories. Do you want to open the '
                                    'directory'
                                    'settings now?',
                                    QMessageBox.Yes | QMessageBox.No) == \
                    QMessageBox.No:
                return
            self.on_actionSettings_triggered()

    def current_plugin(self):
        """ Return the currently selected plugin object
        """
        item = self.pluginsTreeView.currentIndex()
        if not item:
            return None

        return self.plugin_model.data(item, self.plugin_model.DataRole)

    def current_plugin_path(self):
        """ Return the path of the file from which the currently selected
        plugin has been loaded.
        """
        item = self.pluginsTreeView.currentIndex()
        if not item:
            return None

        return self.plugin_model.data(item, self.plugin_model.FilePathRole)

    def get_plugin(self, name):
        """ Get plugin with the given name. Raises a SpykeException if
        multiple plugins with this name exist. Returns None if no such
        plugin exists.
        """
        plugins = self.plugin_model.get_plugins_for_name(name)
        if not plugins:
            return None
        if len(plugins) > 1:
            raise SpykeException('Multiple plugins named "%s" exist!' % name)

        return plugins[0]

    def start_plugin(self, name, current=None, selections=None):
        """ Start first plugin with given name and return result of start()
        method. Raises a SpykeException if not exactly one plugins with
        this name exist.
        """
        plugins = self.plugin_model.get_plugins_for_name(name)
        if not plugins:
            raise SpykeException('No plugin named "%s" exists!' % name)
        if len(plugins) > 1:
            raise SpykeException('Multiple plugins named "%s" exist!' % name)

        if api.config.save_plugin_before_starting:
            e = self.pluginEditorDock.get_editor(plugins[0].source_file)
            if self.pluginEditorDock.file_was_changed(e):
                if not self.pluginEditorDock.save_file(e):
                    return

                plugins = self.plugin_model.get_plugins_for_name(name)
                if not plugins:
                    return None
                if len(plugins) > 1:
                    raise SpykeException(
                        'Multiple plugins named "%s" exist!' % name)

        return self._run_plugin(plugins[0], current, selections)

    def start_plugin_remote(self, name, current=None, selections=None):
        """ Start first plugin with given name remotely. Does not return
        any value. Raises a SpykeException if not exactly one plugins with
        this name exist.
        """
        plugins = self.plugin_model.get_plugins_for_name(name)
        if not plugins:
            raise SpykeException('No plugin named "%s" exists!' % name)
        if len(plugins) > 1:
            raise SpykeException('Multiple plugins named "%s" exist!' % name)

        self._execute_remote_plugin(plugins[0], current, selections)

    def on_file_available(self, available):
        """ Callback when availability of a file for a plugin changes.
        """
        self.actionSavePlugin.setEnabled(available)
        self.actionSavePluginAs.setEnabled(available)

    ##### General housekeeping ###########################################
    @pyqtSignature("")
    def on_actionSettings_triggered(self):
        settings = SettingsWindow(self.selection_path, self.filter_path,
                                  AnalysisPlugin.data_dir, self.remote_script,
                                  self.plugin_paths, self)

        if settings.exec_() == settings.Accepted:
            try:
                self.clean_temporary_selection_files(self.selection_path)
            except:
                pass  # Does not matter if e.g. old directory does not exist
            self.selection_path = settings.selection_path()
            self.filter_path = settings.filter_path()
            self.remote_script = settings.remote_script()
            self.plugin_paths = settings.plugin_paths()
            if self.plugin_paths:
                self.pluginEditorDock.set_default_path(self.plugin_paths[-1])
            self.reload_plugins()

    @pyqtSignature("")
    def on_actionExit_triggered(self):
        self.close()

    @pyqtSignature("")
    def on_actionAbout_triggered(self):
        from .. import __version__

        about = QMessageBox(self)
        about.setWindowTitle(u'About Spyke Viewer')
        about.setTextFormat(Qt.RichText)
        about.setIconPixmap(QPixmap(':/Application/Main'))
        about.setText(
            u'Version ' + __version__ +
            u'<br><br>Spyke Viewer is an application for navigating, '
            u'analyzing and visualizing electrophysiological datasets.<br>'
            u'<br><a href=http://www.ni.tu-berlin.de/software/spykeviewer>'
            u'www.ni.tu-berlin.de/software/spykeviewer</a>'
            u'<br><br>Copyright 2012, 2013 \xa9 Robert Pr\xf6pper<br>'
            u'Neural Information Processing Group<br>'
            u'TU Berlin, Germany<br><br>'
            u'If you use Spyke Viewer in work that leads to a scientific '
            u'publication, please cite:<br>'
            u'Pr\xf6pper, R. and Obermayer, K. (2013). Spyke Viewer: a '
            u'flexible and extensible platform for electrophysiological data '
            u'analysis.<br>'
            u'<i>Front. Neuroinform.</i> 7:26. doi: 10.3389/fninf.2013.00026'
            u'<br><br>Licensed under the terms of the BSD license.<br>'
            u'Icons from the Crystal Project (\xa9 2006-2007 Everaldo Coelho)')
        about.show()

    @pyqtSignature("")
    def on_actionDocumentation_triggered(self):
        webbrowser.open('http://spyke-viewer.readthedocs.org')

    @pyqtSignature("")
    def on_actionSpyke_Repository_triggered(self):
        webbrowser.open('http://spyke-viewer.g-node.org')

    def _get_closed_folders(self):
        if not hasattr(self, 'plugin_model'):
            return []

        folders = self.plugin_model.get_all_folders()
        paths = []
        for f in folders:
            if self.pluginsTreeView.isExpanded(f):
                continue
            path = [f.data()]
            p = f.parent()
            while p.row() >= 0:
                path.append(p.data())
                p = p.parent()

            paths.append('/'.join(reversed(path)))
        return paths

    def clean_temporary_selection_files(self, path):
        """ Remove temporary .temp_..._.sel files from a directory.
        These files are written when executing plugins remotely.
        """
        for f in os.listdir(path):
            if f.startswith('.temp_') and f.endswith('_.sel'):
                os.remove(os.path.join(path, f))

    def closeEvent(self, event):
        """ Saves filters, plugin configs and GUI state.
        """
        if not self.pluginEditorDock.close_all():
            event.ignore()
            return

        # Ensure that selection folder exists
        if not os.path.exists(self.selection_path):
            try:
                os.makedirs(self.selection_path)
            except OSError:
                QMessageBox.critical(
                    self, 'Error', 'Could not create selection directory!')

        self.save_selections_to_file(
            os.path.join(self.selection_path, '.current.sel'))
        self.clean_temporary_selection_files(self.selection_path)

        # Ensure that filters folder exists
        if not os.path.exists(self.filter_path):
            try:
                os.makedirs(self.filter_path)
            except OSError:
                QMessageBox.critical(self, 'Error',
                                     'Could not create filter directory!')
        self.filterDock.save()

        # Save GUI configuration (docks and toolbars)
        settings = QSettings()
        settings.setValue('windowGeometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())

        # Save further configurations
        settings.setValue('pluginPaths', self.plugin_paths)
        settings.setValue('selectionPath', self.selection_path)
        settings.setValue('filterPath', self.filter_path)
        settings.setValue('remoteScript', self.remote_script)

        # Save plugin configurations
        configs = self.get_plugin_configs()
        configs_path = os.path.join(self.data_path, 'plugin_configs.p')
        with open(configs_path, 'w') as f:
            pickle.dump(configs, f)

        # Save closed plugin folders
        settings.setValue('closedPluginFolders', self._get_closed_folders())

        super(MainWindow, self).closeEvent(event)

        # Prevent lingering threads
        self.fileTreeView.setModel(None)
        del self.file_system_model
        self.pluginsTreeView.setModel(None)
        del self.plugin_model
