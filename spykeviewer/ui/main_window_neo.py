import os
from collections import OrderedDict
import logging
import traceback
import inspect

import neo
from neo.io.baseio import BaseIO

from PyQt4.QtCore import (Qt, pyqtSignature, QThread)
from PyQt4.QtGui import (QListWidgetItem, QMessageBox, QApplication,
                         QProgressDialog, QFileDialog)

from spykeutils.progress_indicator import ignores_cancel
from spykeutils.plugin.data_provider_neo import NeoDataProvider
from spykeutils.plugin.data_provider_stored import NeoStoredProvider

from main_window import MainWindow
from ..plugin_framework.data_provider_viewer import NeoViewerProvider


logger = logging.getLogger('spykeviewer')


#noinspection PyCallByClass,PyTypeChecker,PyArgumentList
class MainWindowNeo(MainWindow):
    """ Implements Neo functionality in the main window.
    """
    def __init__(self):
        super(MainWindowNeo, self).__init__()

        self.block_ids = {}
        self.block_names = OrderedDict()  # Just for the display order
        self.block_files = {}
        self.channel_group_names = {}

        # Initialize filters
        self.filter_populate_function = \
            {'Block': self.populate_neo_block_list,
             'Recording Channel': self.populate_neo_channel_list,
             'Recording Channel Group': self.populate_neo_channel_group_list,
             'Segment': self.populate_neo_segment_list,
             'Unit': self.populate_neo_unit_list}

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
        self.navigationNeoDock.setVisible(True)
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

                    if not cl in neo.io.iolist:
                        neo.io.iolist.append(cl)

    def get_letter_id(self, id, small=False):
        """ Return a name consisting of letters given an integer
        """
        if id < 0:
            return ''

        name = ''
        id += 1
        if small:
            start = ord('a') - 1
        else:
            start = ord('A') - 1
        while id >= 1:
            name += str(chr(start + (id % 26)))
            id /= 26
        return name[::-1]

    class LoadWorker(QThread):
        def __init__(self, file_name, indices):
            QThread.__init__(self)
            self.file_name = file_name
            self.indices = indices
            self.blocks = []

        def run(self):
            self.blocks = NeoDataProvider.get_blocks(self.file_name, False)

    @ignores_cancel
    def load_file_callback(self):
        if not self.load_worker:
            self.progress.done()
            return

        # Load worker thread finished
        blocks = self.load_worker.blocks
        if blocks is None:
            logger.error('Could not read file "%s"' %
                         self.load_worker.file_name)

        for block in blocks:
            name = block.name
            if not name or name == 'One segment only':
                name = self.file_system_model.fileName(
                    self.load_worker.indices[0])
            name += ' (%s)' % self.get_letter_id(self.block_index)

            self.block_names[block] = name
            self.block_ids[block] = self.get_letter_id(self.block_index)
            self.block_files[block] = self.load_worker.file_name
            self.block_index += 1

        self.load_progress.reset()
        self.progress.step()

        # Create new load worker thread
        indices = self.load_worker.indices[1:]
        if not indices:
            self.progress.done()
            self.populate_neo_block_list()
            self.load_worker = None
            return

        f = indices[0]
        filepath = self.file_system_model.filePath(f)

        self.load_worker = self.LoadWorker(filepath, indices)
        self.load_progress.setLabelText(filepath)
        self.load_progress.show()
        self.load_worker.finished.connect(self.load_file_callback)
        self.load_worker.terminated.connect(self.load_file_callback)
        self.load_worker.start()

    @ignores_cancel
    def on_loadFilesButton_pressed(self):
        self.neoBlockList.clear()
        self.block_ids.clear()
        self.block_files.clear()
        self.block_names.clear()

        indices = self.fileTreeView.selectedIndexes()
        self.block_index = 0
        self.progress.begin('Loading data files...')
        self.progress.set_ticks(len(indices))

        filepath = self.file_system_model.filePath(indices[0])

        self.load_worker = self.LoadWorker(filepath, indices)
        self.load_progress = QProgressDialog(self.progress)
        self.load_progress.setWindowTitle('Loading File')
        self.load_progress.setLabelText(filepath)
        self.load_progress.setMaximum(0)
        self.load_progress.setCancelButton(None)
        self.load_worker.finished.connect(self.load_file_callback)
        self.load_worker.terminated.connect(self.load_file_callback)
        self.load_progress.show()
        self.load_worker.start()

    def on_fileTreeView_doubleClicked(self, index):
        self.on_loadFilesButton_pressed()

    def refresh_neo_view(self):
        self.set_current_selection(self.provider.data_dict())

    def populate_neo_block_list(self):
        """ Fill the block list with appropriate entries.
            Qt.UserRole: The block itself
        """
        self.neoBlockList.clear()

        filters = self.filterDock.get_active_filters('Block')

        blocks = self.filter_list(self.block_names.keys(), filters)
        for b in blocks:
            if self.is_filtered(b, filters):
                continue

            item = QListWidgetItem(self.block_names[b])
            item.setData(Qt.UserRole, b)
            self.neoBlockList.addItem(item)

        self.neoBlockList.setCurrentRow(0)

    def neo_blocks(self):
        return [t.data(Qt.UserRole) for t in
                self.neoBlockList.selectedItems()]

    def all_neo_blocks(self):
        return self.block_names.keys()

    def neo_block_file_names(self):
        """ Return a dictionary of filenames, indexed by blocks
        """
        return self.block_files

    def populate_neo_segment_list(self):
        self.neoSegmentList.clear()

        filters = self.filterDock.get_active_filters('Segment')

        for item in self.neoBlockList.selectedItems():
            block = item.data(Qt.UserRole)

            segments = self.filter_list(block.segments, filters)
            for i, s in enumerate(segments):
                if self.is_filtered(s, filters):
                    continue

                if s.name:
                    name = s.name + ' (%s-%i)' % (self.block_ids[s.block], i)
                else:
                    name = '%s-%i' % (self.block_ids[s.block], i)

                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, s)
                self.neoSegmentList.addItem(new_item)

        self.neoSegmentList.setCurrentRow(0)

    def neo_segments(self):
        return [t.data(Qt.UserRole) for t in
                self.neoSegmentList.selectedItems()]

    def populate_neo_channel_group_list(self):
        self.neoChannelGroupList.clear()
        self.channel_group_names.clear()

        filters = self.filterDock.get_active_filters(
            'Recording Channel Group')

        for item in self.neoBlockList.selectedItems():
            block = item.data(Qt.UserRole)

            rcgs = self.filter_list(block.recordingchannelgroups, filters)
            for i, rcg in enumerate(rcgs):
                if self.is_filtered(rcg, filters):
                    continue

                self.channel_group_names[rcg] = '%s-%s' % (
                    self.block_ids[rcg.block], self.get_letter_id(i, True))
                if rcg.name:
                    name = rcg.name + ' (%s)' % self.channel_group_names[rcg]
                else:
                    name = self.channel_group_names[rcg]
                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, rcg)
                self.neoChannelGroupList.addItem(new_item)

        self.neoChannelGroupList.setCurrentRow(0)

    def neo_channel_groups(self):
        return [t.data(Qt.UserRole) for t in
                self.neoChannelGroupList.selectedItems()]

    def populate_neo_unit_list(self):
        self.neoUnitList.clear()

        filters = self.filterDock.get_active_filters('Unit')

        for item in self.neoChannelGroupList.selectedItems():
            rcg = item.data(Qt.UserRole)

            units = self.filter_list(rcg.units, filters)
            for i, u in enumerate(units):
                if self.is_filtered(u, filters):
                    continue
                if u.name:
                    name = u.name + ' (%s-%d)' % \
                           (self.channel_group_names[rcg], i)
                else:
                    name = '%s-%d' % (self.channel_group_names[rcg], i)
                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, u)
                self.neoUnitList.addItem(new_item)

    def neo_units(self):
        return [t.data(Qt.UserRole) for t in
                self.neoUnitList.selectedItems()]

    def populate_neo_channel_list(self):
        """ Fill the channel list with appropriate entries. Data slots:
        Qt.UserRole: The channel
        Qt.UserRole+1: The channel index
        """
        self.neoChannelList.clear()

        filters = self.filterDock.get_active_filters(
            'Recording Channel')

        for item in self.neoChannelGroupList.selectedItems():
            channel_group = item.data(Qt.UserRole)

            rcs = self.filter_list(channel_group.recordingchannels, filters)
            for rc in rcs:
                if self.is_filtered(rc, filters):
                    continue

                identifier = '%s.%d' % \
                             (self.channel_group_names[channel_group],
                              rc.index)
                if rc.name:
                    name = rc.name + ' (%s)' % identifier
                else:
                    name = identifier
                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, rc)
                new_item.setData(Qt.UserRole + 1, rc.index)
                self.neoChannelList.addItem(new_item)
                self.neoChannelList.setItemSelected(new_item, True)

    def neo_channels(self):
        return [t.data(Qt.UserRole) for t in
                self.neoChannelList.selectedItems()]

    def on_neoBlockList_itemSelectionChanged(self):
        self.populate_neo_channel_group_list()
        self.populate_neo_segment_list()

    def on_neoChannelGroupList_itemSelectionChanged(self):
        self.populate_neo_channel_list()
        self.populate_neo_unit_list()

    def on_neoBlockList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def on_neoSegmentList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def on_neoChannelGroupList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def on_neoChannelList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def on_neoUnitList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    @pyqtSignature("")
    def on_actionClearCache_triggered(self):
        NeoDataProvider.clear()
        self.neoBlockList.clear()
        self.block_ids.clear()
        self.block_files.clear()
        self.block_names.clear()

        self.populate_neo_block_list()

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
        i = len(self.block_names)
        for b in data['blocks']:
            # File already loaded?
            if unicode(b[1]) in self.block_files.values():
                self.progress.step()
                continue

            QApplication.setOverrideCursor(Qt.WaitCursor)
            blocks = NeoDataProvider.get_blocks(b[1], False)
            QApplication.restoreOverrideCursor()
            if not blocks:
                logger.error('Could not read file "%s"' % b[1])
                self.progress.step()
                continue

            for block in blocks:
                name = block.name
                if not name or name == 'One segment only':
                    name = os.path.basename(b[1])
                name += ' (%s)' % self.get_letter_id(i)

                self.block_names[block] = name
                self.block_ids[block] = self.get_letter_id(i)
                self.block_files[block] = b[1]
                i += 1

            self.progress.step()

        self.progress.done()

        self.populate_neo_block_list()

        block_list = [NeoDataProvider.get_block(b[1], b[0], False)
                      for b in data['blocks']]
        rcg_list = [block_list[rcg[1]].recordingchannelgroups[rcg[0]]
                    for rcg in data['channel_groups']]

        # Select blocks
        for i in self.neoBlockList.findItems('*',
                                             Qt.MatchWrap | Qt.MatchWildcard):
            block = i.data(Qt.UserRole)
            t = [NeoDataProvider.block_indices[block],
                 self.block_files[block]]
            i.setSelected(t in data['blocks'])

        # Select segments
        for i in self.neoSegmentList.findItems('*',
                                               Qt.MatchWrap | Qt.MatchWildcard):
            segment = i.data(Qt.UserRole)
            if not segment.block in block_list:
                i.setSelected(False)
                continue

            seg_idx = segment.block.segments.index(segment)
            block_idx = block_list.index(segment.block)
            i.setSelected([seg_idx, block_idx] in data['segments'])

        # Select recording channel groups
        for i in self.neoChannelGroupList.findItems('*',
                                                    Qt.MatchWrap | Qt.MatchWildcard):
            rcg = i.data(Qt.UserRole)
            if not rcg.block in block_list:
                i.setSelected(False)
                continue

            rcg_idx = rcg.block.recordingchannelgroups.index(rcg)
            block_idx = block_list.index(rcg.block)
            i.setSelected([rcg_idx, block_idx] in data['channel_groups'])

        # Select channels
        rcg_set = set(rcg_list)
        for i in self.neoChannelList.findItems('*',
                                               Qt.MatchWrap | Qt.MatchWildcard):
            i.setSelected(False)
            channel = i.data(Qt.UserRole)
            if not set(channel.recordingchannelgroups).intersection(rcg_set):
                continue

            for rcg in channel.recordingchannelgroups:
                if [rcg.recordingchannels.index(channel),
                        rcg_list.index(rcg)] in data['channels']:
                    i.setSelected(True)
                    break

        # Select units
        for i in self.neoUnitList.findItems('*',
                                            Qt.MatchWrap | Qt.MatchWildcard):
            unit = i.data(Qt.UserRole)
            if unit.recordingchannelgroup not in rcg_list:
                i.setSelected(False)
                continue

            rcg_idx = rcg_list.index(unit.recordingchannelgroup)
            unit_idx = unit.recordingchannelgroup.units.index(unit)
            i.setSelected([unit_idx, rcg_idx] in data['units'])

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
    def on_actionSave_Data_triggered(self):
        d = QFileDialog(self, 'Choose where to save data')
        d.setAcceptMode(QFileDialog.AcceptSave)
        d.setNameFilters(['HDF5 files (*.h5)', 'Matlab files (*.mat)'])
        #d.setDefaultSuffix('h5')
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