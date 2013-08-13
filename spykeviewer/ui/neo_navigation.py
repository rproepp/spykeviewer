from PyQt4.QtGui import (QDockWidget, QMenu, QAction, QMessageBox,
                         QItemSelectionRange, QItemSelection,
                         QStandardItemModel, QStandardItem,
                         QItemSelectionModel)
from PyQt4.QtCore import Qt, pyqtSignal
from spyderlib.utils.qthelpers import get_icon
import neo

from spykeutils.plugin.data_provider_neo import NeoDataProvider
import spykeutils.tools

from neo_navigation_ui import Ui_neoNavigationDock
from .. import api


class NeoNavigationDock(QDockWidget, Ui_neoNavigationDock):
    """ Implements a navigation dock for Neo hierarchies. Tightly coupled
    with :class:`main_window_neo.MainWindowNeo`, the main reason for this
    class to exist is to keep the dock out of the general ui file.
    """

    object_removed = pyqtSignal()  # Signal to remove an object

    def __init__(self, parent):
        QDockWidget.__init__(self, parent)
        self.parent = parent

        self.setupUi(self)

        self.block_model = QStandardItemModel()
        self.segment_model = QStandardItemModel()
        self.channelgroup_model = QStandardItemModel()
        self.channel_model = QStandardItemModel()
        self.unit_model = QStandardItemModel()

        self.neoBlockList.setModel(self.block_model)
        self.neoSegmentList.setModel(self.segment_model)
        self.neoChannelGroupList.setModel(self.channelgroup_model)
        self.neoChannelList.setModel(self.channel_model)
        self.neoUnitList.setModel(self.unit_model)

        self.neoBlockList.doubleClicked.connect(
            lambda x: self._edit_item_annotations(x, self.block_model))
        self.neoSegmentList.doubleClicked.connect(
            lambda x: self._edit_item_annotations(x, self.segment_model))
        self.neoChannelGroupList.doubleClicked.connect(
            lambda x: self._edit_item_annotations(x, self.channelgroup_model))
        self.neoChannelList.doubleClicked.connect(
            lambda x: self._edit_item_annotations(x, self.channel_model))
        self.neoUnitList.doubleClicked.connect(
            lambda x: self._edit_item_annotations(x, self.unit_model))

        self.neoBlockList.selectionModel().selectionChanged.connect(
            self.selected_blocks_changed)
        self.neoChannelGroupList.selectionModel().selectionChanged.connect(
            self.selected_channel_groups_changed)
        self.neoChannelList.selectionModel().selectionChanged.connect(
            self.selected_channels_changed)
        self.neoUnitList.selectionModel().selectionChanged.connect(
            self.selected_units_changed)
        self.neoSegmentList.selectionModel().selectionChanged.connect(
            self.selected_segments_changed)

    def clear(self):
        """ Clear all lists
        """
        self.neoBlockList.clearSelection()
        self.block_model.clear()

    def get_letter_id(self, id_, small=False):
        """ Return a name consisting of letters given an integer
        """
        if id_ < 0:
            return ''

        name = ''
        id_ += 1
        if small:
            start = ord('a')
        else:
            start = ord('A')

        while id_ > 26:
            id_ -= 1
            name += chr(start + (id_ % 26))
            id_ /= 26

        name += chr(start + id_ - 1)

        return name[::-1]

    def ensure_not_filtered(self, objects, all_objects, filters):
        """ Deactivates all filters that prevent the the given sequence
        of objects to be displayed. The passed filter tuple list is
        modified to only include valid filters.

        :param sequence objects: The objects that need to be visible.
        :param sequence all_objects: The whole object list to be filtered,
            including objects that are allowed to be hidden.
        :param sequence filters: A sequence of (Filter, name) tuples.
        """
        objset = set(objects)
        if not objset.issubset(
                set(self.parent.filter_list(all_objects, filters))):
            i = 1
            while i <= len(filters):
                test_filters = filters[:i]
                if objset.issubset(set(self.parent.filter_list(
                        all_objects, test_filters))):
                    i += 1
                else:
                    test_filters[-1][0].active = False
                    filters.pop(i - 1)

        for o in objects:
            i = 0
            while i < len(filters):
                if self.parent.is_filtered(o, [filters[i]]):
                    filters[i][0].active = False
                    filters.pop(i)
                else:
                    i += 1

    def filter_ordered(self, objects, filters):
        """ Filter a sequence of objects with a sequence of filters. Apply
        the filters in the order given by the sequence. Return the filtered
        list.
        """
        for f in filters:
            if f[0].combined:
                objects = self.parent.filter_list(objects, [f])
            else:
                objects = [o for o in objects
                           if not self.parent.is_filtered(o, [f])]
        return objects

    def populate_neo_block_list(self):
        """ Fill the block list with appropriate entries.
        Qt.UserRole: The :class:`neo.Block` object
        """
        self.block_model.clear()

        filters = self.parent.get_active_filters('Block')

        blocks = self.filter_ordered(
            self.parent.block_names.keys(), filters)
        for b in blocks:
            item = QStandardItem(self.parent.block_names[b])
            item.setData(b, Qt.UserRole)
            self.block_model.appendRow(item)

        self.neoBlockList.setCurrentIndex(self.block_model.index(0, 0))
        self.set_blocks_label()
        if not blocks:
            self.selected_blocks_changed()

    def populate_neo_segment_list(self):
        """ Fill the segment list with appropriate entries.
        Qt.UserRole: The :class:`neo.Segment` object
        """
        self.segment_model.clear()

        segments = []
        for b in self.blocks():
            segments.extend(b.segments)

        filters = self.parent.get_active_filters('Segment')
        segments = self.filter_ordered(segments, filters)
        for i, s in enumerate(segments):
            if s.name:
                name = s.name + ' (%s-%i)' % \
                    (self.parent.block_ids[s.block], i)
            else:
                name = '%s-%i' % (self.parent.block_ids[s.block], i)

            new_item = QStandardItem(name)
            new_item.setData(s, Qt.UserRole)
            self.segment_model.appendRow(new_item)

        self.neoSegmentList.setCurrentIndex(self.segment_model.index(0, 0))
        if api.config.autoselect_segments:
            self.neoSegmentList.selectAll()
        self.selected_segments_changed()

    def populate_neo_channel_group_list(self):
        """ Fill the channel group list with appropriate entries.
        Qt.UserRole: The :class:`neo.RecordingChannelGroup` object
        """
        self.neoChannelGroupList.clearSelection()
        self.channelgroup_model.clear()
        self.parent.channel_group_names.clear()

        rcgs = []
        for b in self.blocks():
            rcgs.extend(b.recordingchannelgroups)

        filters = self.parent.get_active_filters(
            'Recording Channel Group')
        rcgs = self.filter_ordered(rcgs, filters)

        for i, rcg in enumerate(rcgs):
            self.parent.channel_group_names[rcg] = '%s-%s' % (
                self.parent.block_ids[rcg.block],
                self.get_letter_id(i, True))
            if rcg.name:
                name = rcg.name + ' (%s)' % \
                                  self.parent.channel_group_names[rcg]
            else:
                name = self.parent.channel_group_names[rcg]
            new_item = QStandardItem(name)
            new_item.setData(rcg, Qt.UserRole)
            self.channelgroup_model.appendRow(new_item)

        self.neoChannelGroupList.setCurrentIndex(
            self.channelgroup_model.index(0, 0))
        if api.config.autoselect_channel_groups:
            self.neoChannelGroupList.selectAll()
        elif not rcgs:
            self.selected_channel_groups_changed()

    def populate_neo_channel_list(self):
        """ Fill the channel list with appropriate entries. Data slots:
        Qt.UserRole: The :class:`neo.RecordingChannel`
        Qt.UserRole+1: The channel index
        """
        self.channel_model.clear()
        channels = set()

        rcs = []
        rc_group_name = {}
        for rcg in self.recording_channel_groups():
            for rc in rcg.recordingchannels:
                if not api.config.duplicate_channels and rc in channels:
                    continue
                channels.add(rc)
                rcs.append(rc)
                rc_group_name[rc] = self.parent.channel_group_names[rcg]

        filters = self.parent.get_active_filters(
            'Recording Channel')
        rcs = self.filter_ordered(rcs, filters)

        for rc in rcs:
            identifier = '%s.%d' % \
                         (rc_group_name[rc],
                          rc.index)
            if rc.name:
                name = rc.name + ' (%s)' % identifier
            else:
                name = identifier

            new_item = QStandardItem(name)
            new_item.setData(rc, Qt.UserRole)
            new_item.setData(rc.index, Qt.UserRole + 1)
            self.channel_model.appendRow(new_item)

        if api.config.autoselect_channels:
            self.neoChannelList.selectAll()
        self.selected_channels_changed()

    def populate_neo_unit_list(self):
        """ Fill the unit list with appropriate entries.
        Qt.UserRole: The :class:`neo.Unit` object
        """
        self.unit_model.clear()

        units = []
        for rcg in self.recording_channel_groups():
            units.extend(rcg.units)

        filters = self.parent.get_active_filters('Unit')
        units = self.filter_ordered(units, filters)

        for i, u in enumerate(units):
            if self.parent.is_filtered(u, filters):
                continue
            if u.name:
                name = u.name + ' (%s-%d)' % \
                       (self.parent.channel_group_names[rcg], i)
            else:
                name = '%s-%d' % (self.parent.channel_group_names[rcg], i)
            new_item = QStandardItem(name)
            new_item.setData(u, Qt.UserRole)
            self.unit_model.appendRow(new_item)

        if api.config.autoselect_units:
            self.neoUnitList.selectAll()
        self.selected_units_changed()

    def set_blocks_label(self):
        self.blocksLabel.setText(
            'Blocks (%d/%d):' % (len(self.neoBlockList.selectedIndexes()),
                                 self.block_model.rowCount()))

    def set_channel_groups_label(self):
        self.channelGroupsLabel.setText(
            'Channel Groups (%d/%d):' % (
                len(self.neoChannelGroupList.selectedIndexes()),
                self.channelgroup_model.rowCount()))

    def selected_blocks_changed(self):
        self.set_blocks_label()
        self.populate_neo_channel_group_list()
        self.populate_neo_segment_list()

    def selected_channel_groups_changed(self):
        self.set_channel_groups_label()
        self.populate_neo_channel_list()
        self.populate_neo_unit_list()

    def selected_channels_changed(self):
        self.channelsLabel.setText(
            'Channels (%d/%d):' % (
                len(self.neoChannelList.selectedIndexes()),
                self.channel_model.rowCount()))

    def selected_units_changed(self):
        self.unitsLabel.setText(
            'Units (%d/%d):' % (
                len(self.neoUnitList.selectedIndexes()),
                self.unit_model.rowCount()))

    def selected_segments_changed(self):
        self.segmentsLabel.setText(
            'Segments (%d/%d):' % (
                len(self.neoSegmentList.selectedIndexes()),
                self.segment_model.rowCount()))

    def _edit_item_annotations(self, index, model):
        api.annotation_editor(model.data(index, Qt.UserRole))

    def remove_selected(self, list_widget):
        """ Remove all selected objects from the given list widget.
        """
        items = list_widget.selectedIndexes()
        if len(items) < 1:
            return
        model = list_widget.model()

        question = ('Do you really want to remove %d %s' %
                    (len(items),
                    type(model.data(items[0], Qt.UserRole)).__name__))
        if len(items) > 1:
            question += 's'
        question += '?'

        if QMessageBox.question(
                self, 'Please confirm', question,
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        for i in list_widget.selectedIndexes():
            data = model.data(i, Qt.UserRole)
            if isinstance(data, neo.Block):
                self.parent.block_names.pop(data)
            else:
                spykeutils.tools.remove_from_hierarchy(data)
            list_widget.selectionModel().select(i, QItemSelectionModel.Deselect)

        self.object_removed.emit()

    def _context_actions(self, list_widget):
        idx = list_widget.currentIndex()
        if not idx:
            return []

        data = list_widget.model().data(idx, Qt.UserRole)

        edit_action = QAction(get_icon('edit.png'),
                              'Edit annotations...', self)
        edit_action.triggered.connect(
            lambda x: self._edit_item_annotations(idx, list_widget.model()))

        delete_name = 'Delete %s' % type(data).__name__
        if len(list_widget.selectedIndexes()) > 1:
            delete_name += 's'
        delete_action = QAction(get_icon('editdelete.png'),
                                delete_name, self)
        delete_action.triggered.connect(
            lambda x:
            self.remove_selected(list_widget))

        return [edit_action, delete_action]

    def on_neoBlockList_customContextMenuRequested(self, pos):
        if not self.neoBlockList.selectedIndexes():
            return
        context_menu = QMenu(self)
        context_menu.addActions(self._context_actions(self.neoBlockList))
        context_menu.popup(self.neoBlockList.mapToGlobal(pos))

    def on_neoSegmentList_customContextMenuRequested(self, pos):
        if not self.neoSegmentList.selectedIndexes():
            return
        context_menu = QMenu(self)
        context_menu.addActions(self._context_actions(self.neoSegmentList))
        context_menu.popup(self.neoSegmentList.mapToGlobal(pos))

    def on_neoChannelGroupList_customContextMenuRequested(self, pos):
        if not self.neoChannelGroupList.selectedIndexes():
            return
        context_menu = QMenu(self)
        context_menu.addActions(self._context_actions(self.neoChannelGroupList))
        context_menu.popup(self.neoChannelGroupList.mapToGlobal(pos))

    def on_neoChannelList_customContextMenuRequested(self, pos):
        if not self.neoChannelList.selectedIndexes():
            return
        context_menu = QMenu(self)
        context_menu.addActions(self._context_actions(self.neoChannelList))
        context_menu.popup(self.neoChannelList.mapToGlobal(pos))

    def on_neoUnitList_customContextMenuRequested(self, pos):
        if not self.neoUnitList.selectedIndexes():
            return
        context_menu = QMenu(self)
        context_menu.addActions(self._context_actions(self.neoUnitList))
        context_menu.popup(self.neoUnitList.mapToGlobal(pos))

    def blocks(self):
        """ Return selected :class:`neo.Block` objects.
        """
        return [self.block_model.data(i, Qt.UserRole) for i in
                self.neoBlockList.selectedIndexes()]

    def segments(self):
        """ Return selected :class:`neo.Segment` objects.
        """
        return [self.segment_model.data(i, Qt.UserRole) for i in
                self.neoSegmentList.selectedIndexes()]

    def recording_channel_groups(self):
        """ Return selected :class:`neo.RecordingChannelGroup` objects.
        """
        return [self.channelgroup_model.data(i, Qt.UserRole) for i in
                self.neoChannelGroupList.selectedIndexes()]

    def recording_channels(self):
        """ Return selected :class:`neo.RecordingChannel` objects.
        """
        return [self.channel_model.data(i, Qt.UserRole) for i in
                self.neoChannelList.selectedIndexes()]

    def units(self):
        """ Return selected :class:`neo.Unit` objects.
        """
        return [self.unit_model.data(i, Qt.UserRole) for i in
                self.neoUnitList.selectedIndexes()]

    def set_selection(self, data):
        """ Set the selected data.
        """
        block_list = []
        for b in data['blocks']:
            cl = None
            rp = None
            if len(b) > 2:
                cl = NeoDataProvider.find_io_class(b[2])
            if len(b) > 3:
                rp = b[3]
            loaded = NeoDataProvider.get_block(
                b[1], b[0], force_io=cl, read_params=rp)
            if loaded is None:
                raise IOError('One of the files contained in the '
                              'selection could not be loaded!')
            block_list.append(loaded)

        block_set = set([(b[0], b[1]) for b in data['blocks']])
        # Select blocks
        self.ensure_not_filtered(block_list, self.parent.block_names.keys(),
                                 self.parent.get_active_filters('Block'))
        self.populate_neo_block_list()
        selection = QItemSelection()
        for i in self.block_model.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            block = i.data(Qt.UserRole)
            t = (NeoDataProvider.block_indices[block],
                 self.parent.block_files[block])

            if t in block_set:
                selection.append(QItemSelectionRange(
                    self.block_model.indexFromItem(i)))
        self.neoBlockList.selectionModel().select(
            selection, QItemSelectionModel.ClearAndSelect)

        # Select segments
        seg_list = [block_list[idx[1]].segments[idx[0]]
                    for idx in data['segments']]
        all_segs = []
        for b in self.blocks():
            all_segs.extend(b.segments)
        self.ensure_not_filtered(seg_list, all_segs,
                                 self.parent.get_active_filters('Segment'))
        self.populate_neo_segment_list()

        selection = QItemSelection()
        for i in self.segment_model.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            segment = i.data(Qt.UserRole)
            if not segment.block in block_list:
                continue

            seg_idx = segment.block.segments.index(segment)
            block_idx = block_list.index(segment.block)
            if [seg_idx, block_idx] in data['segments']:
                selection.append(QItemSelectionRange(
                    self.segment_model.indexFromItem(i)))
        self.neoSegmentList.selectionModel().select(
            selection, QItemSelectionModel.ClearAndSelect)

        # Select recording channel groups
        rcg_list = [block_list[rcg[1]].recordingchannelgroups[rcg[0]]
                    for rcg in data['channel_groups']]
        all_rcgs = []
        for b in self.blocks():
            all_rcgs.extend(b.recordingchannelgroups)
        self.ensure_not_filtered(
            rcg_list, all_rcgs,
            self.parent.get_active_filters('Recording Channel Group'))
        self.populate_neo_channel_group_list()

        selection = QItemSelection()
        for i in self.channelgroup_model.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            rcg = i.data(Qt.UserRole)
            if not rcg.block in block_list:
                continue

            rcg_idx = rcg.block.recordingchannelgroups.index(rcg)
            block_idx = block_list.index(rcg.block)
            if [rcg_idx, block_idx] in data['channel_groups']:
                selection.append(QItemSelectionRange(
                    self.channelgroup_model.indexFromItem(i)))
        self.neoChannelGroupList.selectionModel().select(
            selection, QItemSelectionModel.ClearAndSelect)

        # Select channels
        rc_list = [rcg_list[rc[1]].recordingchannels[rc[0]]
                   for rc in data['channels']]
        all_rcs = []
        for rcg in self.recording_channel_groups():
            for rc in rcg.recordingchannels:
                if not api.config.duplicate_channels and rc in all_rcs:
                    continue
                all_rcs.append(rc)
        self.ensure_not_filtered(
            rc_list, all_rcs,
            self.parent.get_active_filters('Recording Channel'))
        self.populate_neo_channel_list()

        selection = QItemSelection()
        rcg_set = set(rcg_list)
        for i in self.channel_model.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            channel = i.data(Qt.UserRole)
            if not set(channel.recordingchannelgroups).intersection(rcg_set):
                continue

            for rcg in channel.recordingchannelgroups:
                if [rcg.recordingchannels.index(channel),
                        rcg_list.index(rcg)] in data['channels']:
                    selection.append(QItemSelectionRange(
                        self.channel_model.indexFromItem(i)))
                    break
        self.neoChannelList.selectionModel().select(
            selection, QItemSelectionModel.ClearAndSelect)

        # Select units
        unit_list = [rcg_list[u[1]].units[u[0]]
                     for u in data['units']]
        all_units = []
        for rcg in self.recording_channel_groups():
            all_units.extend(rcg.units)
        self.ensure_not_filtered(
            unit_list, all_units,
            self.parent.get_active_filters('Unit'))
        self.populate_neo_unit_list()

        selection = QItemSelection()
        for i in self.unit_model.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            unit = i.data(Qt.UserRole)
            if unit.recordingchannelgroup not in rcg_list:
                continue

            rcg_idx = rcg_list.index(unit.recordingchannelgroup)
            unit_idx = unit.recordingchannelgroup.units.index(unit)
            if [unit_idx, rcg_idx] in data['units']:
                selection.append(QItemSelectionRange(
                    self.unit_model.indexFromItem(i)))
        self.neoUnitList.selectionModel().select(
            selection, QItemSelectionModel.ClearAndSelect)

        self.parent.refresh_filters()