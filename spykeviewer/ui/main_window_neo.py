import os
from collections import OrderedDict
import logging
import traceback
import inspect

import neo
from neo.io.baseio import BaseIO

from PyQt4.QtCore import (Qt, pyqtSignature, QThread, QEvent)
from PyQt4.QtGui import (QMessageBox, QApplication, QActionGroup,
                         QProgressDialog, QFileDialog, QListView,
                         QPushButton, QDialog, QTreeView)
from spyderlib.widgets.dicteditor import DictEditor

from spykeutils.progress_indicator import ignores_cancel
from spykeutils.plugin.data_provider_neo import NeoDataProvider
from spykeutils.plugin.data_provider_stored import NeoStoredProvider

from main_window import MainWindow
from ..plugin_framework.data_provider_viewer import NeoViewerProvider
from neo_navigation import NeoNavigationDock


logger = logging.getLogger('spykeviewer')


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


#noinspection PyCallByClass,PyTypeChecker,PyArgumentList
class MainWindowNeo(MainWindow):
    """ Implements Neo functionality in the main window.
    """
    def __init__(self, parent=None, splash=None):
        super(MainWindowNeo, self).__init__(parent, splash)

        self.block_ids = {}
        self.block_names = OrderedDict()  # Just for the display order
        self.block_files = {}
        self.block_index = 0
        self.was_empty = True
        self.channel_group_names = {}

        # Load mode menu
        self.load_actions = QActionGroup(self)
        self.load_actions.setExclusive(True)
        self.actionFull_Load.setActionGroup(self.load_actions)
        self.actionLazy_Load.setActionGroup(self.load_actions)

        # Neo navigation
        nav = NeoNavigationDock(self)
        self.neoNavigationDock = nav
        self.neoNavigationDock.setObjectName('neoNavigationDock')
        self.addDockWidget(Qt.LeftDockWidgetArea, self.neoNavigationDock)
        self.neoNavigationDock.setVisible(True)
        self.neoNavigationDock.object_removed.connect(self.refresh_neo_view)

        # Initialize filters
        self.filter_populate_function = \
            {'Block': nav.populate_neo_block_list,
             'Recording Channel': nav.populate_neo_channel_list,
             'Recording Channel Group': nav.populate_neo_channel_group_list,
             'Segment': nav.populate_neo_segment_list,
             'Unit': nav.populate_neo_unit_list}

        self.activate_neo_mode()
        self.finish_initialization()

    def get_filter_types(self):
        """ Return a list of filter type tuples as required by
            :class:`filter_dock.FilterDock. Includes filters from Neo.
        """
        l = super(MainWindowNeo, self).get_filter_types()
        l.extend([('Block', 'block'), ('Segment', 'segment'),
                  ('Recording Channel Group', 'rcg'),
                  ('Recording Channel', 'rc'),
                  ('Unit', 'unit')])
        return l

    def get_console_objects(self):
        """ Return a dictionary of objects that should be included in the
        console on startup. These objects will also not be displayed in
        variable explorer. Overriden for Neo imports.
        """
        d = super(MainWindowNeo, self).get_console_objects()
        import quantities
        import neo
        import spykeutils

        d['pq'] = quantities
        d['neo'] = neo
        d['spykeutils'] = spykeutils

        return d

    def set_initial_layout(self):
        self.neoNavigationDock.setVisible(True)
        super(MainWindowNeo, self).set_initial_layout()

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

    def activate_neo_mode(self):
        self.provider = NeoViewerProvider(self)
        self.provider_factory = NeoStoredProvider.from_current_selection
        self.console.interpreter.locals['current'] = self.provider
        if self.ipy_kernel:
            self.ipy_kernel.get_user_namespace()['current'] = self.provider

    def reload_plugins(self, keep_configs=True):
        super(MainWindowNeo, self).reload_plugins(keep_configs)
        self.reload_neo_io_plugins()

    def reload_neo_io_plugins(self):
        # Clean previous plugins
        neo.io.iolist = [io for io in neo.io.iolist
                         if not hasattr(io, '_is_spyke_plugin')]

        for pp in self.plugin_paths:
            for f in os.listdir(pp):
                p = os.path.join(pp, f)

                if os.path.isdir(p):
                    continue
                if not p.lower().endswith('io.py'):
                    continue

                exc_globals = {}
                try:
                    execfile(p, exc_globals)
                except Exception:
                    logger.warning('Error during execution of ' +
                                   'potential Neo IO file ' + p + ':\n' +
                                   traceback.format_exc() + '\n')

                for cl in exc_globals.values():
                    if not inspect.isclass(cl):
                        continue

                    # Should be a subclass of AnalysisPlugin...
                    if not issubclass(cl, BaseIO):
                        continue
                    # ...but should not be AnalysisPlugin (can happen
                    # when directly imported)
                    if cl == BaseIO:
                        continue

                    cl._is_spyke_plugin = True
                    neo.io.iolist.insert(0, cl)

    def get_letter_id(self, id_, small=False):
        """ Return a name consisting of letters given an integer
        """
        return self.neoNavigationDock.get_letter_id(id_, small)

    class LoadWorker(QThread):
        def __init__(self, paths):
            QThread.__init__(self)
            self.paths = paths
            self.blocks = []

        def run(self):
            self.blocks = NeoDataProvider.get_blocks(self.paths[0])

    def load_files(self, file_paths):
        self.progress.begin('Loading data files...')
        self.progress.set_ticks(len(file_paths))

        self.load_worker = self.LoadWorker(file_paths)
        self.load_progress = QProgressDialog(self.progress)
        self.load_progress.setWindowTitle('Loading File')
        self.load_progress.setLabelText(file_paths[0])
        self.load_progress.setMaximum(0)
        self.load_progress.setCancelButton(None)
        self.load_worker.finished.connect(self.load_file_callback)
        self.load_worker.terminated.connect(self.load_file_callback)
        self.load_progress.show()
        self.load_worker.start()

    def edit_annotations(self, data):
        """ Edit annotations of a Neo object.
        """
        editor = DictEditor(self)
        title = 'Edit annotations'
        if data.name:
            title += ' for %s' % data.name
        editor.setup(data.annotations, title)
        editor.accepted.connect(
            lambda: self._editor_ok(data, editor))
        editor.show()
        editor.raise_()
        editor.activateWindow()

    def _editor_ok(self, data, editor):
        data.annotations = editor.get_value()

    @ignores_cancel
    def load_file_callback(self):
        if not self.load_worker:
            self.progress.done()
            return

        # Load worker thread finished
        blocks = self.load_worker.blocks
        if blocks is None:
            logger.error('Could not read file "%s"' %
                         self.load_worker.paths[0])
            self.progress.done()
            self.load_progress.reset()
            return

        for block in blocks:
            name = block.name
            if not name or name == 'One segment only':
                name = os.path.splitext(os.path.basename(
                    self.load_worker.paths[0]))[0]
            name += ' (%s)' % self.get_letter_id(self.block_index)

            self.block_names[block] = name
            self.block_ids[block] = self.get_letter_id(self.block_index)
            self.block_files[block] = self.load_worker.paths[0]
            self.block_index += 1

        self.load_progress.reset()
        self.progress.step()

        # Create new load worker thread
        paths = self.load_worker.paths[1:]
        if not paths:
            self.progress.done()
            if not self.was_empty:
                self.refresh_neo_view()
            else:
                self.neoNavigationDock.populate_neo_block_list()
                self.was_empty = False
            self.load_worker = None
            return

        self.load_worker = self.LoadWorker(paths)
        self.load_progress.setLabelText(paths[0])
        self.load_progress.show()
        self.load_worker.finished.connect(self.load_file_callback)
        self.load_worker.terminated.connect(self.load_file_callback)
        self.load_worker.start()

    @ignores_cancel
    def on_loadFilesButton_pressed(self):
        if not self.block_index:
            self.was_empty = True
        indices = self.fileTreeView.selectedIndexes()
        fs_model = self.file_system_model
        self.load_files([fs_model.filePath(idx) for idx in indices])

    def on_fileTreeView_doubleClicked(self, index):
        if not self.fileTreeView.model().isDir(index):
            self.on_loadFilesButton_pressed()

    def refresh_neo_view(self):
        self.set_current_selection(self.provider.data_dict())

    def neo_blocks(self):
        return self.neoNavigationDock.blocks()

    def all_neo_blocks(self):
        return self.block_names.keys()

    def neo_block_file_names(self):
        """ Return a dictionary of filenames, indexed by blocks
        """
        return self.block_files

    def neo_segments(self):
        return self.neoNavigationDock.segments()

    def neo_channel_groups(self):
        return self.neoNavigationDock.recording_channel_groups()

    def neo_units(self):
        return self.neoNavigationDock.units()

    def neo_channels(self):
        return self.neoNavigationDock.recording_channels()

    @pyqtSignature("")
    def on_actionClearCache_triggered(self):
        if QMessageBox.question(
                self, 'Please confirm',
                'Do you really want to unload all data?',
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        NeoDataProvider.clear()
        self.neoNavigationDock.clear()
        self.block_ids.clear()
        self.block_files.clear()
        self.block_names.clear()
        self.block_index = 0

        self.neoNavigationDock.populate_neo_block_list()

    def add_neo_selection(self, data):
        """ Adds a new neo selection provider with the given data
        """
        self.selections.append(NeoStoredProvider(data, self.progress))

    def set_neo_selection(self, data):
        """ Sets the current selection according to the given provider data
        """
        self.progress.begin('Loading selection data...')
        self.progress.set_ticks(len(data['blocks']))

        # Load blocks which are not currently displayed
        for b in data['blocks']:
            # File already loaded?
            if unicode(b[1]) in self.block_files.values():
                self.progress.step()
                continue

            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                blocks = NeoDataProvider.get_blocks(b[1])
            finally:
                QApplication.restoreOverrideCursor()
            if not blocks:
                logger.error('Could not read file "%s"' % b[1])
                self.progress.step()
                continue

            for block in blocks:
                name = block.name
                if not name or name == 'One segment only':
                    name = os.path.basename(b[1])
                name += ' (%s)' % self.get_letter_id(self.block_index)

                self.block_names[block] = name
                self.block_ids[block] = self.get_letter_id(self.block_index)
                self.block_files[block] = b[1]
                self.block_index += 1
            self.progress.step()

        self.progress.done()

        self.neoNavigationDock.set_selection(data)

    class SaveWorker(QThread):
        def __init__(self, file_name, blocks):
            QThread.__init__(self)
            self.file_name = file_name
            self.blocks = blocks
            self.io = None
            self.terminated.connect(self.cleanup)
            self.finished.connect(self.cleanup)

        def run(self):
            if self.file_name.endswith('.mat'):
                self.io = neo.io.NeoMatlabIO(filename=self.file_name)
                self.io.write_block(self.blocks[0])
            else:
                self.io = neo.io.NeoHdf5IO(filename=self.file_name)
                for block in self.blocks:
                    self.io.save(block)

        def cleanup(self):
            if self.io:
                if hasattr(self.io, 'close'):
                    self.io.close()
                self.io = None

    def _save_blocks(self, blocks, file_name, selected_filter):
        if not blocks:
            QMessageBox.warning(self, 'Cannot save data',
                                'No data to save found!')
            self.progress.done()
            return
        self.progress.set_ticks(0)
        self.progress.setWindowTitle('Writing data...')
        self.progress.set_status('')

        if not file_name.endswith('.h5') and not file_name.endswith('.mat'):
            if selected_filter.endswith('.mat)'):
                file_name += '.mat'
            else:
                file_name += '.h5'

        self.worker = self.SaveWorker(file_name, blocks)
        self.worker.finished.connect(self.progress.done)
        self.progress.canceled.connect(self.worker.terminate)
        self.worker.start()

    @pyqtSignature("")
    def on_actionLoad_Data_triggered(self):
        d = DirFilesDialog(self, 'Choose files or folders to load')

        if not d.exec_():
            return

        self.load_files(d.selectedFiles())

    @pyqtSignature("")
    def on_actionSave_Data_triggered(self):
        d = QFileDialog(self, 'Choose where to save data')
        d.setAcceptMode(QFileDialog.AcceptSave)
        d.setNameFilters(['HDF5 files (*.h5)', 'Matlab files (*.mat)'])
        d.setConfirmOverwrite(True)
        if d.exec_():
            file_name = unicode(d.selectedFiles()[0])
        else:
            return

        self.progress.begin('Collecting data to save...')
        blocks = self.all_neo_blocks()
        self._save_blocks(blocks, file_name, d.selectedFilter())

    @pyqtSignature("")
    def on_actionSave_Selected_Data_triggered(self):
        d = QFileDialog(self, 'Choose where to save selected data')
        d.setAcceptMode(QFileDialog.AcceptSave)
        d.setNameFilters(['HDF5 files (*.h5)', 'Matlab files (*.mat)'])
        #d.setDefaultSuffix('h5')
        d.setConfirmOverwrite(True)
        if d.exec_():
            file_name = unicode(d.selectedFiles()[0])
        else:
            return

        self.progress.begin('Collecting data to save...')
        blocks = self.provider.selection_blocks()
        self._save_blocks(blocks, file_name, d.selectedFilter())

    @pyqtSignature("")
    def on_actionFull_Load_triggered(self):
        NeoDataProvider.lazy_mode = 0

    @pyqtSignature("")
    def on_actionLazy_Load_triggered(self):
        NeoDataProvider.lazy_mode = 1