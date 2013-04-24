from PyQt4.QtGui import (QDockWidget, QMenu, QAction, QMessageBox,
                         QItemSelectionRange, QItemSelection,
                         QStandardItemModel, QStandardItem,
                         QItemSelectionModel)
from PyQt4.QtCore import Qt, pyqtSignal, QModelIndex
from spyderlib.widgets.dicteditor import DictEditor
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

    def populate_neo_block_list(self):
        """ Fill the block list with appropriate entries.
        Qt.UserRole: The :class:`neo.Block` object
        """
        self.block_model.clear()

        filters = self.parent.get_active_filters('Block')

        blocks = self.parent.filter_list(
            self.parent.block_names.keys(), filters)
        for b in blocks:
            if self.parent.is_filtered(b, filters):
                continue

            item = QStandardItem(self.parent.block_names[b])
            item.setData(b, Qt.UserRole)
            self.block_model.appendRow(item)

        self.neoBlockList.setCurrentIndex(self.block_model.index(0, 0))
        self.set_blocks_label()

    def populate_neo_segment_list(self):
        """ Fill the segment list with appropriate entries.
        Qt.UserRole: The :class:`neo.Segment` object
        """
        self.segment_model.clear()

        filters = self.parent.get_active_filters('Segment')

        for index in self.neoBlockList.selectedIndexes():
            block = self.block_model.data(index, Qt.UserRole)

            segments = self.parent.filter_list(block.segments, filters)
            for i, s in enumerate(segments):
                if self.parent.is_filtered(s, filters):
                    continue

                if s.name:
                    name = s.name + ' (%s-%i)' % \
                        (self.parent.block_ids[s.block], i)
                else:
                    name = '%s-%i' % (self.parent.block_ids[s.block], i)

                new_item = QStandardItem(name)
                new_item.setData(s, Qt.UserRole)
                self.segment_model.appendRow(new_item)

        self.neoSegmentList.setCurrentIndex(self.segment_model.index(0, 0))
        self.selected_segments_changed()

    def populate_neo_channel_group_list(self):
        """ Fill the channel group list with appropriate entries.
        Qt.UserRole: The :class:`neo.RecordingChannelGroup` object
        """
        self.neoChannelGroupList.clearSelection()
        self.channelgroup_model.clear()
        self.parent.channel_group_names.clear()

        filters = self.parent.get_active_filters(
            'Recording Channel Group')

        for index in self.neoBlockList.selectedIndexes():
            block = self.block_model.data(index, Qt.UserRole)

            rcgs = self.parent.filter_list(
                block.recordingchannelgroups, filters)
            for i, rcg in enumerate(rcgs):
                if self.parent.is_filtered(rcg, filters):
                    continue

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
        self.set_channel_groups_label()

    def populate_neo_channel_list(self):
        """ Fill the channel list with appropriate entries. Data slots:
        Qt.UserRole: The :class:`neo.RecordingChannel`
        Qt.UserRole+1: The channel index
        """
        self.channel_model.clear()
        channels = set()

        filters = self.parent.get_active_filters(
            'Recording Channel')

        for index in self.neoChannelGroupList.selectedIndexes():
            channel_group = self.channelgroup_model.data(index, Qt.UserRole)

            rcs = self.parent.filter_list(
                channel_group.recordingchannels, filters)
            for rc in rcs:
                if not api.config.duplicate_channels and rc in channels:
                    continue
                if self.parent.is_filtered(rc, filters):
                    continue

                channels.add(rc)
                identifier = '%s.%d' % \
                             (self.parent.channel_group_names[channel_group],
                              rc.index)
                if rc.name:
                    name = rc.name + ' (%s)' % identifier
                else:
                    name = identifier

                new_item = QStandardItem(name)
                new_item.setData(rc, Qt.UserRole)
                new_item.setData(rc.index, Qt.UserRole + 1)
                self.channel_model.appendRow(new_item)

        self.neoChannelList.selectAll()
        self.selected_channels_changed()

    def populate_neo_unit_list(self):
        """ Fill the unit list with appropriate entries.
        Qt.UserRole: The :class:`neo.Unit` object
        """
        self.unit_model.clear()

        filters = self.parent.get_active_filters('Unit')

        for index in self.neoChannelGroupList.selectedIndexes():
            rcg = self.channelgroup_model.data(index, Qt.UserRole)

            units = self.parent.filter_list(rcg.units, filters)
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
        self.edit_annotations(model.data(index, Qt.UserRole))

    def edit_annotations(self, data):
        """ Edit annotations of a Neo object.
        """
        editor = DictEditor(self.parent)
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
        """ Set the selected data. All data in the selection has to be loaded
        before!
        """
        block_list = []
        for b in data['blocks']:
            loaded = NeoDataProvider.get_block(b[1], b[0], False)
            if loaded is None:
                raise IOError('One of the files contained in the '
                              'selection could not be loaded!')
            block_list.append(loaded)
        rcg_list = [block_list[rcg[1]].recordingchannelgroups[rcg[0]]
                    for rcg in data['channel_groups']]

        # Select blocks
        selection = QItemSelection()
        for i in self.block_model.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            block = i.data(Qt.UserRole)
            t = [NeoDataProvider.block_indices[block],
                 self.parent.block_files[block]]

            if t in data['blocks']:
                selection.append(QItemSelectionRange(
                    self.block_model.indexFromItem(i)))
        self.neoBlockList.selectionModel().select(
            selection, QItemSelectionModel.ClearAndSelect)

        # Select segments
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