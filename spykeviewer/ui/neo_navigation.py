from PyQt4.QtGui import (QDockWidget, QListWidgetItem)
from PyQt4.QtCore import Qt

from spykeutils.plugin.data_provider_neo import NeoDataProvider

from neo_navigation_ui import Ui_neoNavigationDock


class NeoNavigationDock(QDockWidget, Ui_neoNavigationDock):
    """ Implements a navigation dock for Neo hierarchies. Tightly coupled
    with :class:`main_window_neo.MainWindowNeo`, the main reason for this
    class to exist is to keep the dock out of the general ui file.
    """
    def __init__(self, parent):
        QDockWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

    def clear(self):
        """ Clear all lists
        """
        self.neoBlockList.clear()

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

    def populate_neo_block_list(self):
        """ Fill the block list with appropriate entries.
        Qt.UserRole: The :class:`neo.Block` object
        """
        self.neoBlockList.clear()

        filters = self.parent.get_active_filters('Block')

        blocks = self.parent.filter_list(
            self.parent.block_names.keys(), filters)
        for b in blocks:
            if self.parent.is_filtered(b, filters):
                continue

            item = QListWidgetItem(self.parent.block_names[b])
            item.setData(Qt.UserRole, b)
            self.neoBlockList.addItem(item)

        self.neoBlockList.setCurrentRow(0)

    def populate_neo_segment_list(self):
        """ Fill the segment list with appropriate entries.
        Qt.UserRole: The :class:`neo.Segment` object
        """
        self.neoSegmentList.clear()

        filters = self.parent.get_active_filters('Segment')

        for item in self.neoBlockList.selectedItems():
            block = item.data(Qt.UserRole)

            segments = self.parent.filter_list(block.segments, filters)
            for i, s in enumerate(segments):
                if self.parent.is_filtered(s, filters):
                    continue

                if s.name:
                    name = s.name + ' (%s-%i)' % \
                        (self.parent.block_ids[s.block], i)
                else:
                    name = '%s-%i' % (self.parent.block_ids[s.block], i)

                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, s)
                self.neoSegmentList.addItem(new_item)

        self.neoSegmentList.setCurrentRow(0)

    def populate_neo_channel_group_list(self):
        """ Fill the channel group list with appropriate entries.
        Qt.UserRole: The :class:`neo.RecordingChannelGroup` object
        """
        self.neoChannelGroupList.clear()
        self.parent.channel_group_names.clear()

        filters = self.parent.get_active_filters(
            'Recording Channel Group')

        for item in self.neoBlockList.selectedItems():
            block = item.data(Qt.UserRole)

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
                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, rcg)
                self.neoChannelGroupList.addItem(new_item)

        self.neoChannelGroupList.setCurrentRow(0)

    def populate_neo_channel_list(self):
        """ Fill the channel list with appropriate entries. Data slots:
        Qt.UserRole: The :class:`neo.RecordingChannel`
        Qt.UserRole+1: The channel index
        """
        self.neoChannelList.clear()

        filters = self.parent.get_active_filters(
            'Recording Channel')

        for item in self.neoChannelGroupList.selectedItems():
            channel_group = item.data(Qt.UserRole)

            rcs = self.parent.filter_list(
                channel_group.recordingchannels, filters)
            for rc in rcs:
                if self.parent.is_filtered(rc, filters):
                    continue

                identifier = '%s.%d' % \
                             (self.parent.channel_group_names[channel_group],
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

    def populate_neo_unit_list(self):
        """ Fill the unit list with appropriate entries.
        Qt.UserRole: The :class:`neo.Unit` object
        """
        self.neoUnitList.clear()

        filters = self.parent.get_active_filters('Unit')

        for item in self.neoChannelGroupList.selectedItems():
            rcg = item.data(Qt.UserRole)

            units = self.parent.filter_list(rcg.units, filters)
            for i, u in enumerate(units):
                if self.parent.is_filtered(u, filters):
                    continue
                if u.name:
                    name = u.name + ' (%s-%d)' % \
                           (self.parent.channel_group_names[rcg], i)
                else:
                    name = '%s-%d' % (self.parent.channel_group_names[rcg], i)
                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, u)
                self.neoUnitList.addItem(new_item)

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

    def blocks(self):
        """ Return selected :class:`neo.Block` objects.
        """
        return [t.data(Qt.UserRole) for t in
                self.neoBlockList.selectedItems()]

    def segments(self):
        """ Return selected :class:`neo.Segment` objects.
        """
        return [t.data(Qt.UserRole) for t in
                self.neoSegmentList.selectedItems()]

    def recording_channel_groups(self):
        """ Return selected :class:`neo.RecordingChannelGroup` objects.
        """
        return [t.data(Qt.UserRole) for t in
                self.neoChannelGroupList.selectedItems()]

    def recording_channels(self):
        """ Return selected :class:`neo.RecordingChannel` objects.
        """
        return [t.data(Qt.UserRole) for t in
                self.neoChannelList.selectedItems()]

    def units(self):
        """ Return selected :class:`neo.Unit` objects.
        """
        return [t.data(Qt.UserRole) for t in
                self.neoUnitList.selectedItems()]

    def set_selection(self, data):
        """ Set the selected data. All data in the selection has to be loaded
        before!
        """
        block_list = [NeoDataProvider.get_block(b[1], b[0], False)
                      for b in data['blocks']]
        rcg_list = [block_list[rcg[1]].recordingchannelgroups[rcg[0]]
                    for rcg in data['channel_groups']]

        # Select blocks
        for i in self.neoBlockList.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            block = i.data(Qt.UserRole)
            t = [NeoDataProvider.block_indices[block],
                 self.parent.block_files[block]]
            i.setSelected(t in data['blocks'])

        # Select segments
        for i in self.neoSegmentList.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            segment = i.data(Qt.UserRole)
            if not segment.block in block_list:
                i.setSelected(False)
                continue

            seg_idx = segment.block.segments.index(segment)
            block_idx = block_list.index(segment.block)
            i.setSelected([seg_idx, block_idx] in data['segments'])

        # Select recording channel groups
        for i in self.neoChannelGroupList.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            rcg = i.data(Qt.UserRole)
            if not rcg.block in block_list:
                i.setSelected(False)
                continue

            rcg_idx = rcg.block.recordingchannelgroups.index(rcg)
            block_idx = block_list.index(rcg.block)
            i.setSelected([rcg_idx, block_idx] in data['channel_groups'])

        # Select channels
        rcg_set = set(rcg_list)
        for i in self.neoChannelList.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
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
        for i in self.neoUnitList.findItems(
                '*', Qt.MatchWrap | Qt.MatchWildcard):
            unit = i.data(Qt.UserRole)
            if unit.recordingchannelgroup not in rcg_list:
                i.setSelected(False)
                continue

            rcg_idx = rcg_list.index(unit.recordingchannelgroup)
            unit_idx = unit.recordingchannelgroup.units.index(unit)
            i.setSelected([unit_idx, rcg_idx] in data['units'])