import os
import sys
import json
from copy import copy

import neo

from spykeutils.progress_indicator import ProgressIndicator
from data_provider import DataProvider

class NeoDataProvider(DataProvider):
    """ Base class for data providers using NEO"""

    # Dictionary of block lists, indexed by (filename, block index) tuples
    loaded_blocks = {}
    block_indices = {} # Dictionary of index in file, indexed by block object

    def __init__(self, name, progress):
        super(NeoDataProvider, self).__init__(name, progress)

    @classmethod
    def clear(cls):
        """ Clears cached blocks
        """
        cls.loaded_blocks.clear()
        cls.block_indices.clear()

    @classmethod
    def get_block(cls, filename, index, lazy=False):
        """ Return the block at the given index in the specified file
        """
        if filename in cls.loaded_blocks:
            return cls.loaded_blocks[filename][index]
        io, blocks = cls._load_neo_file(filename, lazy)
        if io:
            io.close()
        return blocks[index]

    @classmethod
    def get_blocks(cls, filename, lazy=False):
        """ Return a list of blocks loaded from the specified file
        """
        if filename in cls.loaded_blocks:
            return cls.loaded_blocks[filename]
        io, blocks = cls._load_neo_file(filename, lazy)
        if io:
            io.close()
        return blocks

    @classmethod
    def _load_neo_file(cls, filename, lazy):
        """ Returns a NEO io object and a list of contained blocks for a
            file name. This function also caches all loaded blocks
            :Parameters:
                filename : str
                    The full path of the file (relative or absolute)
                lazy : bool
                    Determines if lazy mode is used for NEO io
        """
        # TODO: Enable reading multiple blocks from one file
        if os.path.isdir(filename):
            for io in neo.io.iolist:
                if io.mode == 'dir': # For now, only one directory io exists
                    n_io = io(dirname=filename)
                    block = n_io.read(lazy=lazy)
                    cls.block_indices[block] = 0
                    cls.loaded_blocks[filename] = [block]
                    return n_io, [block]
        else:
            extension = filename.split('.')[-1]
            for io in neo.io.iolist:
                if extension in io.extensions:
                    if io == neo.NeoHdf5IO:
                        n_io = io(filename=filename)
                        blocks = n_io.read_all_blocks(lazy=lazy)
                        for i, b in enumerate(blocks):
                            cls.block_indices[b] = i
                        cls.loaded_blocks[filename] = blocks
                        return n_io, blocks
                    try:
                        n_io = io(filename=filename)
                        block = n_io.read(lazy=lazy)
                        cls.block_indices[block] = 0
                        cls.loaded_blocks[filename] = [block]
                        return n_io, [block]
                    except Exception:
                        sys.stderr.write('Load error with '+str(io)+
                                         ' for file '+filename+'\n')
                        continue
        return None, None

    @staticmethod
    def _get_data_from_viewer(viewer):
        """ Return a dictionary with selection information from viewer
        """
        # The links in this data format are based list indices
        data = {}
        data['type'] = 'Neo'

        # Block entry: (Index of block in file, file location of block)
        block_list = []
        block_indices = {}
        selected_blocks = viewer.neo_blocks()
        block_files = viewer.neo_block_file_names()
        for b in selected_blocks:
            block_indices[b] = len(block_list)
            block_list.append([NeoDataProvider.block_indices[b],
                               block_files[b]])
        data['blocks'] = block_list

        # Recording channel group entry:
        # (Index of rcg in block, index of block)
        rcg_list = []
        rcg_indices = {}
        selected_rcg = viewer.neo_channel_groups()
        for rcg in selected_rcg:
            rcg_indices[rcg] = len(rcg_list)
            idx = rcg.block.recordingchannelgroups.index(rcg)
            rcg_list.append([idx, block_indices[rcg.block]])
        data['channel_groups'] = rcg_list

        # Recording channel entry: (Index of channel in rcg, index of rcg)
        # There can be multiple channel entries for one channel object, if
        # it is part of multiple channel groups
        channel_list = []
        selected_channels = viewer.neo_channels()
        for c in selected_channels:
            for rcg in c.recordingchannelgroups:
                if rcg in rcg_indices:
                    idx = rcg.recordingchannels.index(c)
                    channel_list.append([idx, rcg_indices[rcg]])
        data['channels'] = channel_list

        # Segment entry: (Index of segment in block, index of block)
        segment_list = []
        segment_indices = {}
        selected_segments = viewer.neo_segments()
        for s in selected_segments:
            segment_indices[s] = len(segment_list)
            idx = s.block.segments.index(s)
            segment_list.append([idx, block_indices[s.block]])
        data['segments'] = segment_list

        # Unit entry: (Index of uinit in rcg, index of rcg)
        unit_list = []
        selected_units = viewer.neo_units()
        for u in selected_units:
            segment_indices[u] = len(segment_list)
            rcg_id = None if u.recordingchannelgroup is None\
            else u.recordingchannelgroup.units.index(u)
            rcg = rcg_indices[u.recordingchannelgroup]\
            if u.recordingchannelgroup else None
            unit_list.append([rcg_id, rcg])
        data['units'] = unit_list

        return data

    def blocks(self):
        """ Return a list of selected Block objects
        """
        return []

    def segments(self):
        """ Return a list of selected Segment objects
        """
        return []

    def recording_channel_groups(self):
        """ Return a list of selected
        """
        return []

    def recording_channels(self):
        """ Return a list of selected recording channel indices
        """
        return []

    def recording_channel_objects(self):
        """ Return a list of selected RecordingChannel objects
        """
        rcgs = self.recording_channel_groups()
        channel_ids = self.recording_channels()
        channels = []
        for rcg in rcgs:
            channels.extend([c for c in rcg.recordingchannels
                             if c.index in channel_ids])
        return channels

    def units(self):
        """ Return a list of selected Unit objects
        """
        return []

    def spike_trains(self):
        """ Return a list of SpikeTrain objects.
        """
        trains = []
        units = self.units()
        for s in self.segments():
            trains.extend([t for t in s.spiketrains if t.unit in units])
        for u in self.units():
            trains.extend([t for t in u.spiketrains if t.segment is None])

        return trains

    def spike_trains_by_unit(self):
        """ Return a dictionary (indexed by Unit) of lists of
        SpikeTrain objects.
        """
        trains = {}
        segments = self.segments()
        for u in self.units():
            trains[u] = [t for t in u.spiketrains if t.segment in segments]

        nonetrains = []
        for s in self.segments():
            nonetrains.extend([t for t in s.spiketrains if t.unit is None])
        if nonetrains:
            trains[self.no_unit] = nonetrains

        return trains

    def _active_block(self, old):
        block = copy(old)

        block.segments = []
        selected_segments = self.segments()
        for s in old.segments:
            if s in selected_segments:
                segment = copy(s)
                segment.block = block
                block.segments.append(segment)

        block.recordingchannelgroups = []
        selected_rcgs = self.recording_channel_groups()
        selected_channels = self.recording_channels()
        selected_units = self.units()
        for old_rcg in old.recordingchannelgroups:
            if old_rcg in selected_rcgs:
                rcg = copy(old_rcg)

                rcg.recordingchannels = []
                for c in old_rcg.recordingchannels:
                    if not c in selected_channels:
                        continue
                    channel = copy(c)
                    channel.recordingchannelgroups = copy(
                        c.recordingchannelgroups)
                    channel.recordingchannelgroups.insert(
                        channel.recordingchannelgroups.index(old_rcg), rcg)
                    channel.recordingchannelgroups.remove(old_rcg)
                    rcg.recordingchannels.append(channel)

                rcg.units = []
                for u in old_rcg.units:
                    if not u in selected_units:
                        continue

                    unit = copy(u)
                    unit.recordingchannelgroup = rcg
                    rcg.units.append(unit)

                rcg.block = block
                block.recordingchannelgroups.append(rcg)

        return block

    def selection_blocks(self):
        """ Return a list of selected blocks.
        """
        return [self._active_block(b) for b in self.blocks()]


    def spike_trains_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        SpikeTrain objects.
        """
        trains = {}
        units = self.units()
        for s in self.segments():
            trains[s] = [t for t in s.spiketrains if t.unit in units]

        nonetrains = []
        for u in self.units():
            nonetrains.extend([t for t in u.spiketrains if t.segment is None])
        if nonetrains:
            trains[self.no_segment] = nonetrains

        return trains

    def spike_trains_by_unit_and_segment(self):
        """ Return a dictionary (indexed by Unit) of dictionaries
        (indexed by Segment) of SpikeTrain objects.
        """
        trains = {}
        segments = self.segments()
        for u in self.units():
            for s in segments:
                segtrains = [t for t in u.spiketrains if t.segment == s]
                if segtrains:
                    if u not in trains:
                        trains[u] = {}
                    trains[u][s] = segtrains[0]
            nonetrains = [t for t in u.spiketrains if t.segment is None]
            if nonetrains:
                if u not in trains:
                    trains[u] = {}
                trains[u][self.no_segment] = nonetrains[0]

        nonetrains = {}
        for s in self.segments():
            segtrains = [t for t in s.spiketrains if t.unit is None]
            if segtrains:
                nonetrains[s] = segtrains[0]
        if nonetrains:
            trains[self.no_unit] = nonetrains

        return trains

    def spikes(self):
        """ Return a list of Spike objects.
        """
        spikes = []
        units = self.units()
        for s in self.segments():
            spikes.extend([t for t in s.spikes if t.unit in units])
        for u in self.units():
            spikes.extend([t for t in u.spikes if t.segment is None])

        return spikes

    def spikes_by_unit(self):
        """ Return a dictionary (indexed by Unit) of lists of
        Spike objects.
        """
        spikes = {}
        segments = self.segments()
        for u in self.units():
            spikes[u] = [t for t in u.spikes if t.segment in segments]

        nonespikes = []
        for s in self.segments():
            nonespikes.extend([t for t in s.spikes if t.unit is None])
        if nonespikes:
            spikes[self.no_unit] = nonespikes

        return spikes

    def spikes_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        Spike objects.
        """
        spikes = {}
        units = self.units()
        for s in self.segments():
            spikes[s] = [t for t in s.spikes if t.unit in units]

        nonespikes = []
        for u in self.units():
            nonespikes.extend([t for t in u.spikes if t.segment is None])
        if nonespikes:
            spikes[self.no_segment] = nonespikes

        return spikes

    def spikes_by_unit_and_segment(self):
        """ Return a dictionary (indexed by Unit) of dictionaries
        (indexed by Segment) of Spike objects.
        """
        spikes = {}
        segments = self.segments()
        for u in self.units():
            for s in segments:
                segtrains = [t for t in u.spikes if t.segment == s]
                if segtrains:
                    if u not in spikes:
                        spikes[u] = {}
                    spikes[u][s] = segtrains[0]
            nonespikes = [t for t in u.spikes if t.segment is None]
            if nonespikes:
                if u not in spikes:
                    spikes[u] = {}
                spikes[u][self.no_segment] = nonespikes[0]

        nonespikes = {}
        for s in self.segments():
            segtrains = [t for t in s.spikes if t.unit is None]
            if segtrains:
                nonespikes[s] = segtrains[0]
        if nonespikes:
            spikes[self.no_unit] = nonespikes

        return spikes

    def events(self):
        """ Return a dictionary (indexed by Segment) of lists of
        Event objects.
        """
        ret = {}
        for s in self.segments():
            ret[s] = s.events
        return ret

    def labeled_events(self, label):
        """ Return a dictionary (indexed by Segment) of lists of Event
        objects with the given label.
        """
        ret = {}
        for s in self.segments():
            ret[s] = [e for e in s.events if e.label == label]
        return ret

    def epochs(self):
        """ Return a dictionary (indexed by Segment) of lists of
        Epoch objects.
        """
        ret = {}
        for s in self.segments():
            ret[s] = s.epochs
        return ret

    def labeled_epochs(self, label):
        """ Return a dictionary (indexed by Segment) of lists of Epoch
        objects with the given label.
        """
        ret = {}
        for s in self.segments():
            ret[s] = [e for e in s.epochs if e.label == label]
        return ret

    def num_analog_signals(self):
        """ Return the number of AnalogSignal objects.
        """
        return len(self.analog_signals())

    def analog_signals(self):
        """ Return a list of AnalogSignal objects.
        """
        signals = []
        channels = self.recording_channels()
        for s in self.segments():
            signals.extend([t for t in s.analogsignals
                           if t.recordingchannel in channels])
        for u in self.recording_channels():
            signals.extend([t for t in u.analogsignals if t.segment is None])

        return signals

    def analog_signals_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        AnalogSignal objects.
        """
        signals = {}
        channels = self.recording_channels()
        for s in self.segments():
            signals[s] = [t for t in s.analogsignals
                          if t.recordingchannel in channels]

        nonesignals = []
        for c in channels:
            nonesignals.extend([t for t in c.analogsignals
                                if t.segment is None])
        if nonesignals:
            signals[self.no_segment] = nonesignals

        return signals

    def analog_signals_by_channel(self):
        """ Return a dictionary (indexed by RecordingChannel) of lists
        of AnalogSignal objects.
        """
        signals = {}
        segments = self.segments()
        for c in self.recording_channels():
            signals[c] = [t for t in c.analogsignals
                          if t.segment in segments]

        nonesignals = []
        for s in segments:
            nonesignals.extend([t for t in s.analogsignals
                                if t.recordingchannel is None])
        if nonesignals:
            signals[self.no_segment] = nonesignals

        return signals

    def analog_signals_by_channel_and_segment(self):
        """ Return a dictionary (indexed by RecordingChannel) of
        dictionaries (indexed by Segment) of AnalogSignal objects.
        """
        signals = {}
        segments = self.segments()
        for c in self.recording_channels():
            for s in segments:
                segsignals = [t for t in c.analogsignals if t.segment == s]
                if segsignals:
                    if c not in signals:
                        signals[c] = {}
                    signals[c][s] = segsignals[0]
            nonesignals = [t for t in c.analogsignals if t.segment is None]
            if nonesignals:
                if c not in signals:
                    signals[c] = {}
                signals[c][self.no_segment] = nonesignals[0]

        nonesignals = {}
        for s in self.segments():
            segsignals = [t for t in s.analogsignals
                          if t.recordingchannel is None]
            if segsignals:
                nonesignals[s] = segsignals[0]
        if nonesignals:
            signals[self.no_channel] = nonesignals

        return signals

    def num_analog_signal_arrays(self):
        """ Return the number of AnalogSignalArray objects.
        """
        return len(self.analog_signal_arrays())

    def analog_signal_arrays(self):
        """ Return a list of AnalogSignalArray objects.
        """
        signals = []
        channelgroups = self.recording_channel_groups()
        for s in self.segments():
            signals.extend([t for t in s.analogsignalarrays
                            if t.recordingchannelgroup in channelgroups])
        for u in channelgroups:
            signals.extend([t for t in u.analogsignalarrays
                            if t.segment is None])

        return signals

    def analog_signal_arrays_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        AnalogSignalArray objects.
        """
        signals = {}
        channelgroups = self.recording_channel_groups()
        for s in self.segments():
            signals[s] = [t for t in s.analogsignalarrays
                          if t.recordingchannel in channelgroups]

        nonesignals = []
        for c in channelgroups:
            nonesignals.extend([t for t in c.analogsignalarrays
                                if t.segment is None])
        if nonesignals:
            signals[self.no_segment] = nonesignals

        return signals

    def analog_signal_arrays_by_channelgroup(self):
        """ Return a dictionary (indexed by RecordingChannelGroup) of
        lists of AnalogSignalArray objects.
        """
        signals = {}
        segments = self.segments()
        for c in self.recording_channel_groups():
            signals[c] = [t for t in c.analogsignalarrays
                          if t.segment in segments]

        nonesignals = []
        for s in segments:
            nonesignals.extend([t for t in s.analogsignalarrays
                                if t.recordingchannelgroup is None])
        if nonesignals:
            signals[self.no_channelgroup] = nonesignals

        return signals

    def analog_signal_arrays_by_channelgroup_and_segment(self):
        """ Return a dictionary (indexed by RecordingChannelGroup) of
        dictionaries (indexed by Segment) of AnalogSignalArray objects.
        """
        signals = {}
        segments = self.segments()
        for c in self.recording_channel_groups():
            for s in segments:
                segsignals = [t for t in c.analogsignalarrays
                              if t.segment == s]
                if segsignals:
                    if c not in signals:
                        signals[c] = {}
                    signals[c][s] = segsignals[0]
            nonesignals = [t for t in c.analogsignalarrays
                           if t.segment is None]
            if nonesignals:
                if c not in signals:
                    signals[c] = {}
                signals[c][self.no_segment] = nonesignals[0]

        nonesignals = {}
        for s in self.segments():
            segsignals = [t for t in s.analogsignalarrays
                          if t.recordingchannelgroup is None]
            if segsignals:
                nonesignals[s] = segsignals[0]
        if nonesignals:
            signals[self.no_channelgroup] = nonesignals

        return signals

class NeoViewerProvider(NeoDataProvider):
    def __init__(self, viewer, name='Current'):
        super(NeoViewerProvider, self).__init__(name, viewer.progress)
        self.viewer = viewer

    def blocks(self):
        """ Return a list of selected Block objects
        """
        return self.viewer.neo_blocks()

    def segments(self):
        """ Return a list of selected Segment objects
        """
        return self.viewer.neo_segments()

    def recording_channel_groups(self):
        """ Return a list of selected
        """
        return self.viewer.neo_channel_groups()

    def recording_channels(self):
        """ Return a list of selected recording channel indices
        """
        return self.viewer.neo_channels()

    def units(self):
        """ Return a list of selected Unit objects
        """
        return self.viewer.neo_units()

    def data_dict(self):
        """ Return a dictionary with all information to serialize the object
        """
        data = NeoViewerProvider._get_data_from_viewer(self.viewer)
        data['name'] = self.name
        return data

class NeoStoredProvider(NeoDataProvider):
    def __init__(self, data, progress=ProgressIndicator()):
        super(NeoStoredProvider, self).__init__(data['name'], progress)
        self.data = data
        self.block_cache = None

    @classmethod
    def from_current_selection(cls, name, viewer):
        """ Create new NeoStoredProvider from current viewer selection
        """
        data = cls._get_data_from_viewer(viewer)
        data['name'] = name
        return cls(data, viewer.progress)

    @classmethod
    def from_file(cls, file_name, progress=ProgressIndicator()):
        """ Create new DBStoredProvider from JSON file
        """
        data = json.load(file_name)
        return cls(data, progress)

    def save(self, file_name):
        """ Save selection to JSON file
        """
        f = open(file_name, 'w')
        json.dump(self.data, f, sort_keys=True, indent=4)
        f.close()

    def data_dict(self):
        """ Return a dictionary with all information to serialize the object
        """
        self.data['name'] = self.name
        return self.data

    def blocks(self):
        """ Return a list of selected Block objects
        """
        if self.block_cache is None:
            self.block_cache = [NeoDataProvider.get_block(b[1], b[0])
                           for b in self.data['blocks']]
        return self.block_cache

    def segments(self):
        """ Return a list of selected Segment objects
        """
        blocks = self.blocks()
        segments = []
        for s in self.data['segments']:
            segments.append(blocks[s[1]].segments[s[0]])
        return segments

    def recording_channel_groups(self):
        """ Return a list of selected
        """
        blocks = self.blocks()
        rcgs = []
        for rcg in self.data['channel_groups']:
            rcgs.append(blocks[rcg[1]].recordingchannelgroups[rcg[0]])
        return rcgs

    def recording_channels(self):
        """ Return a list of selected recording channel indices
        """
        return self.data['channels']

    def units(self):
        """ Return a list of selected Unit objects
        """
        rcgs = self.recording_channel_groups()
        units = []
        for u in self.data['units']:
            units.append(rcgs[u[1]].units[u[0]])
        return units

# Enable automatic creation of NeoStoredProvider objects
DataProvider._factories['Neo'] = NeoStoredProvider