import os
from collections import OrderedDict
import logging
import pickle
import copy
import json

import neo

from PyQt4.QtCore import (Qt, pyqtSignature, QThread)
from PyQt4.QtGui import (QMessageBox, QApplication,
                         QProgressDialog, QFileDialog)
try:  # Support for spyder < 3
    from spyderlib.widgets.dicteditor import DictEditor
except ImportError:
    from spyderlib.widgets.variableexplorer.collectionseditor import \
         CollectionsEditor as DictEditor

from spykeutils import SpykeException
from spykeutils.progress_indicator import ignores_cancel
from spykeutils.plugin.data_provider_neo import NeoDataProvider
from spykeutils.plugin.data_provider_stored import NeoStoredProvider
from spykeutils.plugin import io_plugin

from .main_window import MainWindow
from ..plugin_framework.data_provider_viewer import NeoViewerProvider
from .neo_navigation import NeoNavigationDock
from .dir_files_dialog import DirFilesDialog
from . import io_settings
from .. import api

logger = logging.getLogger('spykeviewer')


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
        self.io_write_params = {}

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
            self.ipy_kernel.push({'current': self.provider})

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

                try:
                    io_plugin.load_from_file(p)
                except SpykeException, e:
                    logger.warning(str(e))

        # Populate IO list
        self.neoIOComboBox.clear()
        iolabels = []

        for io in neo.io.iolist:
            if io.name:
                iolabels.append((io.name, io))
            else:
                iolabels.append((io.__name__, io))

        iolabels.sort(key=lambda x: x[0].lower())
        self.neoIOComboBox.addItem('By extension')
        self.neoIOComboBox.setItemData(0, None)
        self.neoIOComboBox.addItems([l[0] for l in iolabels])

        for i, l in enumerate(iolabels):
            self.neoIOComboBox.setItemData(i + 1, l[1])

        # Delete stale IO configs
        for p in self.io_write_params.keys():
            if p not in neo.io.iolist:
                del self.io_write_params[p]
        for p in NeoDataProvider.io_params.keys():
            if p not in neo.io.iolist:
                del NeoDataProvider.io_params[p]

    def get_letter_id(self, id_, small=False):
        """ Return a name consisting of letters given an integer
        """
        return self.neoNavigationDock.get_letter_id(id_, small)

    class LoadWorker(QThread):
        def __init__(self, paths):
            QThread.__init__(self)
            self.paths = paths
            self.blocks = []
            self.error = None

        def run(self):
            try:
                self.blocks = NeoDataProvider.get_blocks(self.paths[0])
            except Exception as e:
                self.error = e
                raise

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
            QMessageBox.critical(
                self, 'File could not be loaded',
                'Could not read "%s": No suitable IO found.' %
                self.load_worker.paths[0])
            logger.error('Could not read "%s": No suitable IO found.' %
                         self.load_worker.paths[0])
            self.progress.done()
            self.load_progress.reset()
            self.raise_()
            return

        if self.load_worker.error:
            QMessageBox.critical(
                self, 'File could not be loaded',
                'While loading "%s", the following error occured:'
                '\n\n%s\n%s\n\nSee the console for more details.' % (
                    self.load_worker.paths[0],
                    type(self.load_worker.error).__name__,
                    str(self.load_worker.error)))
            self.progress.done()
            self.load_progress.reset()
            self.raise_()
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
                cl = None
                rp = None
                if len(b) > 2:
                    cl = NeoDataProvider.find_io_class(b[2])
                if len(b) > 3:
                    rp = b[3]
                blocks = NeoDataProvider.get_blocks(
                    b[1], force_io=cl, read_params=rp)
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
        def __init__(self, file_name, blocks, io, params):
            QThread.__init__(self)
            self.file_name = file_name
            self.blocks = blocks
            self.io = io(filename=file_name)
            self.params = params
            self.terminated.connect(self.cleanup)
            self.finished.connect(self.cleanup)

        def run(self):
            if hasattr(self.io, 'write_all_blocks'):
                self.io.write(self.blocks, **self.params)
            else:
                if neo.Block not in self.io.writeable_objects:
                    logger.warning('%s does not support writing blocks.' %
                                   (self.io.name or type(self.io).__name__))
                    if not len(self.blocks[0].segments) == 1:
                        logger.warning('Please select a single block with a'
                                       'single Segment.\nAborting...')
                    else:
                        logger.warning(
                            'Writing only first segment of first file...')
                        self.io.write(self.blocks[0], **self.params)
                else:
                    if len(self.blocks) > 1:
                        logger.warning(
                            '%s does not support writing multiple blocks.\n'
                            'Writing only first block...')
                    self.io.write(self.blocks[0], **self.params)

        def cleanup(self):
            if self.io:
                if hasattr(self.io, 'close'):
                    self.io.close()
                self.io = None

    def _save_blocks(self, blocks, file_name, io):
        if not blocks:
            QMessageBox.warning(self, 'Cannot save data',
                                'No data to save found!')
            self.progress.done()
            return
        self.progress.set_ticks(0)
        self.progress.setWindowTitle('Writing data...')
        self.progress.set_status('')

        if not os.path.splitext(file_name)[1]:  # No previous file extension
            if len(io.extensions) == 1:  # Unambiguous extension for this io
                file_name += '.' + io.extensions[0]

        self.worker = self.SaveWorker(file_name, blocks, io,
                                      self.io_write_params.get(io, {}))
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
        path, io = self._save_data_dialog('Choose where to save data')
        if path is None:
            return

        self.progress.begin('Collecting data to save...')
        blocks = self.all_neo_blocks()
        self._save_blocks(blocks, path, io)

    @pyqtSignature("")
    def on_actionSave_Selected_Data_triggered(self):
        path, io = self._save_data_dialog(
            'Choose where to save selected data')
        if path is None:
            return

        self.progress.begin('Collecting data to save...')
        blocks = self.provider.selection_blocks()
        self._save_blocks(blocks, path, io)

    def _get_writeable_formats(self):
        """ Return a list of name filters for save dialog and a dictionary
        that maps name filters to IO classes.
        """
        filters = []
        d = {}
        for io in neo.io.iolist:
            if not io.is_writable:
                continue
            filters.append('%s (%s)' % (
                io.name or io.__name__,
                ' '.join(['*.' + ext for ext in io.extensions])))
            d[filters[-1]] = io
        return filters, d

    def _save_data_dialog(self, title):
        """ Create a save dialog for data. Return the filename and selected IO
        if the user wants to save, (None, None) if the dialog was canceled.

        :param str title: Dialog title
        """
        dialog = QFileDialog(self, title)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        name_filters, io_mapping = self._get_writeable_formats()
        dialog.setNameFilters(name_filters)
        dialog.setConfirmOverwrite(True)
        if not dialog.exec_():
            return None, None

        return unicode(dialog.selectedFiles()[0]), \
               io_mapping[dialog.selectedNameFilter()]

    @pyqtSignature("")
    def on_actionFull_Load_triggered(self):
        NeoDataProvider.data_lazy_mode = 0

    @pyqtSignature("")
    def on_actionLazy_Load_triggered(self):
        NeoDataProvider.data_lazy_mode = 1

    @pyqtSignature("")
    def on_actionCached_Lazy_Load_triggered(self):
        NeoDataProvider.data_lazy_mode = 2

    @pyqtSignature("")
    def on_actionFull_triggered(self):
        NeoDataProvider.cascade_lazy = False

    @pyqtSignature("")
    def on_actionLazy_triggered(self):
        NeoDataProvider.cascade_lazy = True

    @pyqtSignature("int")
    def on_neoIOComboBox_currentIndexChanged(self, index):
        if index > 0:
            NeoDataProvider.forced_io = self.neoIOComboBox.itemData(index)
            self.configureIOButton.setEnabled(
                io_settings.has_ui_params(NeoDataProvider.forced_io))
        else:
            NeoDataProvider.forced_io = None
            self.configureIOButton.setEnabled(False)

    @pyqtSignature("")
    def on_configureIOButton_pressed(self):
        io = NeoDataProvider.forced_io
        d = io_settings.ParamDialog(
            io, NeoDataProvider.io_params.get(io, {}),
            self.io_write_params.get(io, {}), self)

        if d.exec_():
            NeoDataProvider.io_params[io] = d.get_read_params()
            self.io_write_params[io] = d.get_write_params()

    def _execute_remote_plugin(self, plugin, current=None, selections=None):
        sl = list()

        if current is None:
            sl.append(self.provider_factory('__current__', self).data_dict())
        else:
            d = copy.copy(current.data_dict())
            d['name'] = '__current__'
            sl.append(d)
        if selections is None:
            selections = self.selections

        for s in selections:
            sl.append(s.data_dict())

        io_plugin_files = []
        transform_path = getattr(api.config, 'remote_path_transform',
                                 lambda x: x)
        for s in sl:
            if s['type'] != 'Neo':
                continue
            for b in s['blocks']:
                if len(b) > 2:
                    io = NeoDataProvider.find_io_class(b[2])
                    if io is None:
                        raise NameError('Error executing remote plugin: '
                                        '%s is not a known IO class!' % b[2])
                    if getattr(io, '_is_spyke_plugin', False):
                        io_plugin_files.append(io._python_file)
                b[1] = transform_path(b[1])

        selections = json.dumps(sl, sort_keys=True, indent=2)
        config = pickle.dumps(plugin.get_parameters())
        name = type(plugin).__name__
        path = plugin.source_file
        self.send_plugin_info(name, path, selections, config, io_plugin_files)

    def closeEvent(self, event):
        super(MainWindowNeo, self).closeEvent(event)

        NeoDataProvider.clear()
