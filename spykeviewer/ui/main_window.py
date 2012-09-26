import os
import sys
import json
import logging

from PyQt4.QtGui import (QMainWindow, QMessageBox,
                         QApplication, QFileDialog, QInputDialog,
                         QLineEdit, QMenu, QDrag, QPainter, QPen,
                         QPalette, QDesktopServices, QFont)
from PyQt4.QtCore import (Qt, pyqtSignature, SIGNAL, QMimeData,
                          QSettings, QCoreApplication)

from spyderlib.widgets.internalshell import InternalShell
from spyderlib.widgets.externalshell.namespacebrowser import NamespaceBrowser
from spyderlib.widgets.sourcecode.codeeditor import CodeEditor

from spykeutils.plugin.data_provider import DataProvider
from spykeutils.plugin.analysis_plugin import AnalysisPlugin

from main_ui import Ui_MainWindow
from progress_indicator_dialog import ProgressIndicatorDialog


logger = logging.getLogger('spykeviewer')
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
logger.addHandler(ch)

#noinspection PyCallByClass,PyTypeChecker,PyArgumentList
class MainWindow(QMainWindow, Ui_MainWindow):
    """ The main window of SpikeViewer
    """

    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)

        QCoreApplication.setOrganizationName('SpykeUtils')
        QCoreApplication.setApplicationName('Spyke Viewer')

        self.setupUi(self)
        self.dir = os.getcwd()
        self.console = None
        self.progress = ProgressIndicatorDialog(self)
        self.provider_factory = DataProvider
        self.selections = []
        self.provider = None
        self.plugin_paths = []
        self.init_python()

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

        # Docks
        self.setCentralWidget(None)
        self.update_view_menu()

    def update_view_menu(self):
        if hasattr(self, 'menuView'):
            a = self.menuView.menuAction()
            self.mainMenu.removeAction(a)
        self.menuView = self.createPopupMenu()
        self.menuView.setTitle('View')
        self.mainMenu.insertMenu(self.menuHelp.menuAction(), self.menuView)

    def restore_state(self):
        settings = QSettings()
        if not settings.contains('windowGeometry') or\
           not settings.contains('windowState'):
            self.set_initial_layout()
        else:
            self.restoreGeometry(settings.value('windowGeometry'))
            self.restoreState(settings.value('windowState'))

        if not settings.contains('pluginPaths'):
            if hasattr(sys, 'frozen'):
                module_path = os.path.dirname(sys.executable)
            else:
                file_path = os.path.abspath(os.path.dirname(__file__))
                module_path = os.path.dirname(os.path.dirname(file_path))
            plugin_path = os.path.join(module_path, 'plugins')
            if os.path.isdir(plugin_path):
                self.plugin_paths.append(plugin_path)
        else:
            paths = settings.value('pluginPaths')
            if paths is None:
                self.plugin_paths = []
            else:
                self.plugin_paths = paths

        if not settings.contains('selectionPath'):
            data_path = QDesktopServices.storageLocation(
                QDesktopServices.DataLocation)
            self.selection_path = os.path.join(data_path, 'selections')
        else:
            self.selection_path = settings.value('selectionPath')

        if not settings.contains('dataPath'):
            data_path = QDesktopServices.storageLocation(
                QDesktopServices.DataLocation)
            AnalysisPlugin.data_dir = os.path.join(data_path, 'data')
        else:
            AnalysisPlugin.data_dir = settings.value('dataPath')

        if not settings.contains('remoteScript'):
            if hasattr(sys, 'frozen'):
                path = os.path.dirname(sys.executable)
            else:
                import spykeutils
                path = os.path.dirname(spykeutils.__file__)
                path = os.path.join(os.path.abspath(path), 'plugin')
            self.remote_script = os.path.join(path, 'start_plugin.py')
        else:
            self.remote_script = settings.value('remoteScript')

        self.load_current_selection()

    def set_initial_layout(self):
        self.setGeometry(self.x(), self.y(), 800, 750)
        self.navigationNeoDock.setVisible(True)

        self.removeDockWidget(self.filterDock)
        self.removeDockWidget(self.analysisDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filterDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.analysisDock)
        self.tabifyDockWidget(self.filterDock, self.analysisDock)
        self.filterDock.setVisible(True)
        self.analysisDock.setVisible(True)

        self.consoleDock.setVisible(False)
        self.variableExplorerDock.setVisible(False)
        self.historyDock.setVisible(False)
        self.tabifyDockWidget(self.consoleDock, self.variableExplorerDock)
        self.tabifyDockWidget(self.variableExplorerDock, self.historyDock)

    def init_python(self):
        class StreamDuplicator():
            def __init__(self, out_list):
                self.outs = out_list

            def write(self, s):
                for o in self.outs:
                    o.write(s)

        # Fixing autocompletion bugs in the internal shell
        class FixedInternalShell(InternalShell):
            def __init__(self, *args, **kwargs):
                super(FixedInternalShell, self).__init__(*args, **kwargs)

            def show_completion_list(self, completions,
                                           completion_text="",
                                           automatic=True):
                if completions is None:
                    return
                super(FixedInternalShell, self).show_completion_list(
                    completions, completion_text, automatic)

            def get_dir(self, objtxt):
                if not isinstance(objtxt, (str, unicode)):
                    return
                return super(FixedInternalShell, self).get_dir(objtxt)

        # Console
        import numpy
        import scipy
        try:
            import matplotlib.pyplot as plt
            pltmsg = 'matplotlib.pyplot as plt, guiqwt.pyplot as guiplt, '
        except ImportError:
            import guiqwt.pyplot as plt
            pltmsg = 'guiqwt.pyplot as plt, '
        import guiqwt.pyplot as guiplt
        import quantities
        import neo
        import spykeutils
        plt.ion()
        guiplt.ion()

        ns = {'current': self.provider, 'selections': self.selections,
              'np': numpy, 'sp': scipy, 'plt': plt, 'guiplt': guiplt,
              'pq': quantities, 'neo': neo, 'spykeutils': spykeutils}
        msg = ('current and selections can be used as in the start() ' +
        ' method of a plugin.\n\n' +
        'Modules imported at startup: numpy as np, scipy as sp, ' +
        pltmsg + 'quantities as pq, neo, spykeutils')

        self.console = FixedInternalShell(self.consoleDock, namespace=ns,
            multithreaded=False, message=msg, max_line_count=1000)
        #self.console.clear_terminal()

        font = QFont("Courier new")
        font.setStyleHint(font.TypeWriter, font.PreferDefault)
        font.setPointSize(9)
        self.console.set_font(font)
        self.console.set_codecompletion_auto(True)
        self.console.set_calltips(True)
        self.console.setup_calltips(size=600, font=font)
        self.console.setup_completion(size=(370, 240), font=font)

        self.consoleDock.setWidget(self.console)

        # Variable browser
        self.browser = NamespaceBrowser(self.variableExplorerDock)
        self.browser.set_shellwidget(self.console)
        self.browser.setup(check_all=True, exclude_private=True,
            exclude_uppercase=False, exclude_capitalized=False,
            exclude_unsupported=False, truncate=False, minmax=False,
            collvalue=False, remote_editing=False, inplace=False,
            autorefresh=False,
            excluded_names=['execfile', 'guiplt', 'help', 'neo', 'np', 'pq',
                            'plt', 'guiplt', 'raw_input', 'runfile', 'sp',
                            'spykeutils'])
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

        # Duplicate stdout and stderr
        sys.stdout = StreamDuplicator([sys.stdout, sys.__stdout__])
        sys.stderr = StreamDuplicator([sys.stderr, sys.__stderr__])

    def _append_python_history(self):
        self.browser.refresh_table()
        self.history.append('\n' + self.console.history[-1])
        self.history.set_cursor_position('eof')

    @pyqtSignature("")
    def on_actionExit_triggered(self):
        self.close()

    @pyqtSignature("")
    def on_actionAbout_triggered(self):
        QMessageBox.about(self, u'About Spyke Viewer',
            u'Spyke Viewer is an application for navigating, ' +
            u'analyzing and visualizing electrophysiological datasets.\n\n' +
            u'Copyright 2012 \xa9 Robert Pr\xf6pper\n' +
            u'Neural Information Processing Group\n' +
            u'TU Berlin, Germany\n\n' +
            u'Licensed under the terms of the BSD license.\n\n' +
            u'Icons from the Crystal Project ' +
            u'(\xa9 2006-2007 Everaldo Coelho)')

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
                lambda sel=s:self.on_selection_load(sel))

            a = m.addAction('Save')
            self.connect(a, SIGNAL('triggered()'),
                lambda sel=s:self.on_selection_save(sel))

            a = m.addAction('Rename')
            self.connect(a, SIGNAL('triggered()'),
                lambda sel=s:self.on_selection_rename(sel))

            a = m.addAction('Remove')
            self.connect(a, SIGNAL('triggered()'),
                lambda sel=s:self.on_selection_remove(sel))

    def on_selection_load(self, selection):
        self.set_current_selection(selection.data_dict())

    def on_selection_save(self, selection):
        i = self.selections.index(selection)
        self.selections[i] = self.provider_factory(
            self.selections[i].name, self)
        self.populate_selection_menu()

    def on_selection_clear(self):
        if QMessageBox.question(self, 'Confirmation',
            'Do you really want to remove all selections?',
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        del self.selections[:]
        self.populate_selection_menu()

    def on_selection_rename(self, selection):
        (name, ok) = QInputDialog.getText(self, 'Edit selection name',
            'New name:', QLineEdit.Normal, selection.name)
        if ok and name:
            selection.name = name
            self.populate_selection_menu()

    def on_selection_remove(self, selection):
        if QMessageBox.question(self, 'Confirmation',
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
        sl = list() # Selection list, current selection as first item
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
            self.progress.done()
            QMessageBox.critical(self, 'Error loading selection',
                str(type(e).__name__) + ': ' + str(e).decode('utf8'))
        finally:
            self.populate_selection_menu()

    def on_menuFile_triggered(self, action):
        if action == self.actionSave_selection:
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
        elif action == self.actionLoad_selection:
            d = QFileDialog(self, 'Choose selection file',
                self.selection_path)
            d.setAcceptMode(QFileDialog.AcceptOpen)
            d.setFileMode(QFileDialog.ExistingFile)
            d.setNameFilter("Selection files (*.sel)")
            if d.exec_():
                filename = str(d.selectedFiles()[0])
            else:
                return

            self.load_selections_from_file(filename)

    def set_current_selection(self, data):
        if data['type'] == 'Neo':
            self.set_neo_selection(data)
        else:
            raise NotImplementedError(
                'This version of Spyke Viewer only supports Neo selections!')

    def add_selection(self, data):
        if data['type'] == 'Neo':
            self.add_neo_selection(data)
        else:
            raise NotImplementedError(
                'This version of Spyke Viewer only supports Neo selections!')

    def closeEvent(self, event):
        """ Saves filters and GUI state
        """
        # Ensure that filters folder exists
        if not os.path.exists(self.selection_path):
            try:
                os.makedirs(self.selection_path)
            except OSError:
                QMessageBox.critical(self, 'Error',
                    'Could not create selection directory!')

        self.save_selections_to_file(
            os.path.join(self.selection_path, '.current.sel'))

        # Save GUI configuration (docks and toolbars)
        settings = QSettings()
        settings.setValue('windowGeometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())

        # Save further configurations
        settings.setValue('pluginPaths', self.plugin_paths)
        settings.setValue('selectionPath', self.selection_path)
        settings.setValue('filterPath', self.filter_path)
        settings.setValue('remoteScript', self.remote_script)

        super(MainWindow, self).closeEvent(event)

    def on_variableExplorerDock_visibilityChanged(self, visible):
        if visible:
            self.browser.refresh_table()

    def on_historyDock_visibilityChanged(self, visible):
        if visible:
            self.history.set_cursor_position('eof')
