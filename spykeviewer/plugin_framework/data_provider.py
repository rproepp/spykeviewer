import neo

class DataProvider(object):
    """ Defines all methods that should be implemented by a
    selection/data provider class.

    A `DataProvider` encapsulates
    access to a selection of data. It can be used by plugins to
    acesss data currently selected in the GUI or in saved selections.
    It also contains an attribute `progress`, a
    :class:`spykeutils.progress_indicator.ProgressIndicator` that
    can be used to report the progress of an operation (and is used
    by methods of this class if they can lead to processing times
    of half a second or more).

    This class serves as an abstract base class and should not be
    instantiated."""
    _factories = {}
    no_unit = neo.Unit(name='No Unit')
    no_segment = neo.Segment(name='No segment')
    no_channel = neo.RecordingChannel(name='No recording channel')
    no_channelgroup = neo.RecordingChannelGroup(name='No recording channel group')
    no_unit.annotate(unique_id=-1)
    no_segment.annotate(unique_id=-1)
    no_channel.annotate(unique_id=-1)
    no_channelgroup.annotate(unique_id=-1)

    def __init__(self, name, progress):
        self.name = name
        self.progress = progress

    def _invert_indices(self, dictionary):
        """ Invert the indices of a dictionary of dictionaries.
        """
        dict_type = type(dictionary)
        ret = dict_type()
        for i1 in dictionary:
            for i2 in dictionary[i1]:
                if not i2 in ret:
                    ret[i2] = dict_type()
                ret[i2][i1] = dictionary[i1][i2]
        return ret

    def selection_blocks(self):
        """ Return a list of selected blocks.

        The returned blocks will contain references to all other selected
        elements further down in the object hierarchy, but no references to
        elements which are not selected. The returned hierarchy is volatile,
        meaning that changes made to it will not persist. The main purpose
        of this function is to provide an object hierarchy that can be
        saved to a neo file. It is not recommended to use it for data
        processing, as the whole selection has to be loaded.
        """
        return []

    def spike_trains(self):
        """ Return a list of SpikeTrain objects.
        """
        return []

    def spike_trains_by_unit(self):
        """ Return a dictionary (indexed by Unit) of lists of
        SpikeTrain objects.

        If spike trains not attached to a Unit are selected, their
        dicionary key will be ``DataProvider.no_unit``.
        """
        return {}

    def spike_trains_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        SpikeTrain objects.

        If spike trains not attached to a Segment are selected, their
        dictionary key will be ``DataProvider.no_segment``.
        """
        return {}

    def spike_trains_by_unit_and_segment(self):
        """ Return a dictionary (indexed by Unit) of dictionaries
        (indexed by Segment) of SpikeTrain objects.

        If there are multiple spike trains in one Segment for the same Unit,
        only the first will be contained in the returned dictionary. If spike
        trains not attached to a Unit or Segment are selected, their
        dictionary key will be ``DataProvider.no_unit`` or
        ``DataProvider.no_segment``, respectively.
        """
        return {}

    def spike_trains_by_segment_and_unit(self):
        """ Return a dictionary (indexed by Unit) of dictionaries
        (indexed by Segment) of SpikeTrain objects.

        If there are multiple spike trains in one Segment for the same Unit,
        only the first will be contained in the returned dictionary. If spike
        trains not attached to a Unit or Segment are selected, their
        dictionary key will be ``DataProvider.no_unit`` or
        ``DataProvider.no_segment``, respectively.
        """
        return self._invert_indices(self.spike_trains_by_unit_and_segment())

    def spikes(self):
        """ Return a list of Spike objects.
        """
        return []

    def spikes_by_unit(self):
        """ Return a dictionary (indexed by Unit) of lists of
        Spike objects.

        If spikes not attached to a Unit are selected, their
        dicionary key will be ``DataProvider.no_unit``.
        """
        return {}

    def spikes_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        Spike objects.

        If spikes not attached to a Segment are selected, their
        dictionary key will be ``DataProvider.no_segment``.
        """
        return {}

    def spikes_by_unit_and_segment(self):
        """ Return a dictionary (indexed by Unit) of dictionaries
        (indexed by Segment) of Spike objects.

        If there are multiple spikes in one Segment for the same Unit,
        only the first will be contained in the returned dictionary. If
        spikes not attached to a Unit or Segment are selected, their
        dictionary key will be ``DataProvider.no_unit`` or
        ``DataProvider.no_segment``, respectively.
        """
        return {}

    def spikes_by_segment_and_unit(self):
        """ Return a dictionary (indexed by Segment) of dictionaries
        (indexed by Unit) of lists of Spike objects.

        If spikes not attached to a Unit or Segment are selected, their
        dictionary key will be ``DataProvider.no_unit`` or
        ``DataProvider.no_segment``, respectively.
        """
        return self._invert_indices(self.spikes_by_unit_and_segment())

    def events(self):
        """ Return a dictionary (indexed by Segment) of lists of
        Event objects.
        """
        return {}

    def labeled_events(self, label):
        """ Return a dictionary (indexed by Segment) of lists of Event
        objects with the given label.

        :param str label: The name of the Event objects to be returnded
        """
        return []

    def epochs(self):
        """ Return a dictionary (indexed by Segment) of lists of
        Epoch objects.
        """
        return {}

    def labeled_epochs(self, label):
        """ Return a dictionary (indexed by Segment) of lists of Epoch
        objects with the given label.

        :param str label: The name of the Epoch objects to be returnded
        """
        return []

    def num_analog_signals(self):
        """ Return the number of AnalogSignal objects.
        """
        return 0

    def analog_signals(self):
        """ Return a list of AnalogSignal objects.
        """
        return []

    def analog_signals_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        AnalogSignal objects.

        If analog signals not attached to a Segment are selected, their
        dictionary key will be ``DataProvider.no_segment``.
        """
        return {}

    def analog_signals_by_channel(self):
        """ Return a dictionary (indexed by RecordingChannel) of lists
        of AnalogSignal objects.

        If analog signals not attached to a RecordingChannel are selected,
        their dictionary key will be ``DataProvider.no_channel``.
        """
        return {}

    def analog_signals_by_channel_and_segment(self):
        """ Return a dictionary (indexed by RecordingChannel) of
        dictionaries (indexed by Segment) of AnalogSignal objects.

        If analog signals not attached to a Segment or
        RecordingChannel are selected, their dictionary key will be
        ``DataProvider.no_segment`` or ``DataProvider.no_channel``,
        respectively.
        """
        return {}

    def analog_signals_by_segment_and_channel(self):
        """ Return a dictionary (indexed by Segment) of
        dictionaries (indexed by RecordingChannel) of AnalogSignal objects.

        If analog signals not attached to a Segment or
        RecordingChannel are selected, their dictionary key will be
        ``DataProvider.no_segment`` or ``DataProvider.no_channel``,
        respectively.
        """
        return self._invert_indices(
            self.analog_signals_by_channel_and_segment())

    def num_analog_signal_arrays(self):
        """ Return the number of AnalogSignalArray objects.
        """
        return 0

    def analog_signal_arrays(self):
        """ Return a list of AnalogSignalArray objects.
        """
        return []

    def analog_signal_arrays_by_segment(self):
        """ Return a dictionary (indexed by Segment) of lists of
        AnalogSignalArray objects.

        If analog signals arrays not attached to a Segment are selected,
        their dictionary key will be ``DataProvider.no_segment``.
        """
        return {}

    def analog_signal_arrays_by_channelgroup(self):
        """ Return a dictionary (indexed by RecordingChannelGroup) of
        lists of AnalogSignalArray objects.

        If analog signals arrays not attached to a RecordingChannel are
        selected, their dictionary key will be
        ``DataProvider.no_channelgroup``.
        """
        return {}

    def analog_signal_arrays_by_channelgroup_and_segment(self):
        """ Return a dictionary (indexed by RecordingChannelGroup) of
        dictionaries (indexed by Segment) of AnalogSignalArray objects.

        If there are multiple analog signals in one RecordingChannel for
        the same Segment, only the first will be contained in the returned
        dictionary. If analog signal arrays not attached to a Segment or
        RecordingChannelGroup are selected, their dictionary key will be
        ``DataProvider.no_segment`` or ``DataProvider.no_channelgroup``,
        respectively.
        """
        return {}

    def analog_signal_arrays_by_segment_and_channelgroup(self):
        """ Return a dictionary (indexed by RecordingChannelGroup) of
        dictionaries (indexed by Segment) of AnalogSignalArray objects.

        If there are multiple analog signals in one RecordingChannel for
        the same Segment, only the first will be contained in the returned
        dictionary. If analog signal arrays not attached to a Segment or
        RecordingChannelGroup are selected, their dictionary key will be
        ``DataProvider.no_segment`` or ``DataProvider.no_channelgroup``,
        respectively.
        """
        return self._invert_indices(
            self.analog_signal_arrays_by_channelgroup_and_segment())

    def data_dict(self):
        """ Return a dictionary with all information to serialize the
        object.
        """
        return {}

    @classmethod
    def from_data(cls, data, progress=None):
        """ Create a new `DataProvider` object from a dictionary. This
        method is mostly for internal use.

        The respective type of `DataProvider` (e.g.
        :class:`spykeviewer.plugin_framework.data_provider_neo.DataProviderNeo`
        has to be imported in the environment where this function is
        called.

        :param dict data: A dictionary containing data from a `DataProvider`
            object, as returned by :func:`data_dict`.
        :param ProgressIndicator progress: The object where loading progress
            will be indicated.
        """
        if progress:
            return cls._factories[data['type']](data, progress)
        return cls._factories[data['type']](data)